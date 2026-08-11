import datetime
import requests
import random
from collections import Counter
import simplejson as json

from .models import QuestionAnswerState, Room, WorkerAssignment, Question, ChatMessage, QuestionMeta, QuestionSet, ActionRecord
from .settings import MAX_LEVEL, DATASET, get_set_params, AUTOQUIT_LIMIT

import logging
logger = logging.getLogger(__name__)


def advance_progress(room):
    set_params = get_set_params(room.level)
    if room.finished:
        return False, None, None
    if room.question_set_progress < (set_params.normals + set_params.honeypots) - 1:
        room.question_set_progress += 1
        room.question_start_time = datetime.datetime.now(datetime.timezone.utc)
        room.has_deadline = False
        return False, None, None
    else:
        room.has_deadline = False
        old_question_set = room.question_set
        question_meta = QuestionMeta.objects.get(question_meta_id=DATASET)
        questions = sorted(list(Question.objects.all().filter(question_meta_id=question_meta).values_list('question_id', flat=True)))

        new_set_params = get_set_params(room.level + 1)

        random.seed(room.room_id)
        random.shuffle(questions)
        size = new_set_params.honeypots + new_set_params.normals
        offset = (room.level + 1) * size
        selected_question_ids = questions[offset:offset + size]
        logger.info("Selected ids {}".format(selected_question_ids))
        honeypot_ids = random.sample(list(range(size)), new_set_params.honeypots)

        question_set = QuestionSet(question_meta_id=question_meta,
                                    question_ids=",".join(str(q) for q in selected_question_ids),
                                    honeypot_indexes=",".join(str(q) for q in honeypot_ids))

        question_set.room_id  = room.room_id
        question_set.level = room.level + 1
        question_set.save()

        action = ActionRecord(action_type=ActionRecord.ActionType.LEND, worker=str(room.room_id), payload=json.dumps({
            "level": room.level,
        }))
        action.save()

        room.level += 1
        room.question_set = question_set
        room.question_set_progress = 0
        room.question_start_time = datetime.datetime.now(datetime.timezone.utc)
        return True, room.level-1, old_question_set


def next_question(room):
    question_id = [int(v) for v in room.question_set.question_ids.split(",")][room.question_set_progress]
    state_obj = QuestionAnswerState.objects.select_for_update().get(room_id=room.room_id, question_id=question_id)
    state = json.loads(state_obj.state)

    workers = WorkerAssignment.objects.all().filter(room_id=room.room_id).filter(state=WorkerAssignment.AssignmentState.ASSIGNED)

    workers_to_quit = set()
    for w in workers:
        if w.worker_id in state:
            w.missed_questions = 0
        else:
            w.missed_questions += 1
            logger.info("Worker {} missed question".format(w.login))
        if w.missed_questions >= AUTOQUIT_LIMIT:
            logger.info("Worker {} should quit".format(w.login))
            workers_to_quit.add(w)

    WorkerAssignment.objects.bulk_update(workers, fields=["missed_questions"])

    for w in workers_to_quit:
        w.state = WorkerAssignment.AssignmentState.DONE
        w.quit_level = room.level
        w.quit_reason = "Autoquit"
        logger.info("Worker {} quits. Level {}".format(w, w.quit_level))
        w.save()
        action = ActionRecord(action_type=ActionRecord.ActionType.ACTION, worker=str(w.worker_id), payload="quit")
        action.save()

    need_score, level_to_score, question_set = advance_progress(room)

    scores = {}
    if need_score:
        scores = score(room, level_to_score, question_set)

    if room.level > MAX_LEVEL and not room.finished:
        room.finished = True
        workers = WorkerAssignment.objects.all().filter(room_id=room.room_id)

        for w in workers:
            w.state = WorkerAssignment.AssignmentState.DONE
            action = ActionRecord(action_type=ActionRecord.ActionType.ATRAN, worker=str(w.worker_id), payload="done")
            action.save()
        WorkerAssignment.objects.bulk_update(workers, fields=["state"])

    return scores, [w.worker_id for w in workers_to_quit]


def score(room: Room, level: int, question_set: QuestionSet):
    questions = [int(v) for v in question_set.question_ids.split(",")]
    honeypots = set(int(i) for i in question_set.honeypot_indexes.split(","))

    logger.info("Questions {}".format(questions))
    logger.info("Honeypots {}".format(honeypots))

    workers = WorkerAssignment.objects.all().filter(room_id=room.room_id).filter(state=WorkerAssignment.AssignmentState.ASSIGNED)
    set_params = get_set_params(level)

    worker_accuracy_deltas = {w.worker_id: 0 for w in workers}
    room_delta = 0
    room_agreement_delta = 0
    room_accuracy_delta = 0

    for idx, q_id in enumerate(questions):
        state_obj = QuestionAnswerState.objects.select_for_update().get(room_id=room.room_id, question_id=q_id)
        state = json.loads(state_obj.state)
        is_honeypot = idx in honeypots

        if is_honeypot:
            correct_answer = Question.objects.get(question_id=q_id).correct_answer

            correct_count = 0
            for w in workers:
                if w.worker_id in state and state[w.worker_id][0] == correct_answer and state[w.worker_id][1]:
                    correct_count += 1

            logger.info("Giving score for honeypot. HP score is {}".format(set_params.accuracy_score))
            score = int(float(set_params.accuracy_score) / len(workers) * correct_count)

            room.score += score
            room.bonus_score += score
            room_delta += score
            room_accuracy_delta += score

            for w in workers:
                w.bonus_score += score
                w.score += score

                if w.worker_id in state and state[w.worker_id][0] == correct_answer and state[w.worker_id][1]:
                    worker_accuracy_deltas[w.worker_id] += score / correct_count

        room.score += set_params.base_score
        room_delta += set_params.base_score
        for w in workers:
            w.score += set_params.base_score
            if w.worker_id in state and state[w.worker_id][1]:
                logger.info("Giving normal score {}".format(set_params.base_score))
            else:
                logger.info("Worker {} didn't confirm answer =(".format(w.worker_id))


        ans_counter = Counter()
        for w in state:
            if state[w][1]:
                ans_counter[state[w][0]] += 1

        max_count = max(ans_counter.values())
        if max_count >= (len(workers) // 2 + 1):
            if max_count == len(workers):
                bonus = set_params.agreement_score
            else:
                bonus = set_params.majority_score

            room.score += bonus
            room.bonus_score += bonus
            room_delta += bonus
            for w in workers:
                w.score += bonus
                w.bonus_score += bonus
            room_agreement_delta += bonus

        logger.info("Max answer count: " + str(max(ans_counter.values())))


    WorkerAssignment.objects.bulk_update(workers, fields=["score"])
    return {w.worker_id: (
        room_delta,
        room_agreement_delta,
        set_params.agreement_score * set_params.question_count,
        room_accuracy_delta,
        set_params.accuracy_score * set_params.honeypots,
        worker_accuracy_deltas[w.worker_id],
        ) for w in workers
    }
