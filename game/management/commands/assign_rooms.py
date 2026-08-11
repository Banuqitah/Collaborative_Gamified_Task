import datetime
import random
import asyncio

from game.settings import get_set_params

from django.core.management.base import BaseCommand
from django.db import transaction
from game.models import WorkerAssignment, Room, Question, QuestionMeta, QuestionSet, QuestionAnswerState, ActionRecord
from game.consumers import make_worker_group_name, make_vote_group_name
from channels.layers import get_channel_layer
from django.forms.models import model_to_dict


import game.settings as cfg
from game.score import next_question

import logging
logger = logging.getLogger(__name__)


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def create_room(assignment_batch, question_ids, question_meta):
    set_params = get_set_params(1)

    question_set = QuestionSet(question_meta_id=question_meta,
                               question_ids="",
                               honeypot_indexes="")
    question_set.save()
    new_room = Room(question_set=question_set)
    new_room.save()

    random.seed(new_room.room_id)
    question_ids = sorted(question_ids)
    random.shuffle(question_ids)
    selected_question_ids = question_ids[:set_params.honeypots + set_params.normals]
    honeypot_ids = random.sample(list(range(set_params.honeypots + set_params.normals)), set_params.honeypots)
    logger.info("Honeypot ids {}".format(honeypot_ids))
    question_set.question_ids = ",".join(str(q) for q in selected_question_ids)
    question_set.honeypot_indexes = ",".join(str(q) for q in honeypot_ids)
    question_set.room_id  = new_room.room_id
    question_set.level = 1
    question_set.save()

    answer_states = []
    for q in question_ids:
        answer_states.append(QuestionAnswerState(room=new_room, question_id=q))
    QuestionAnswerState.objects.bulk_create(answer_states)

    logger.info("Created room {}".format(new_room.room_id))
    for a in assignment_batch:
        a.room_id = new_room.room_id
        a.state = WorkerAssignment.AssignmentState.ASSIGNED
        action = ActionRecord(action_type=ActionRecord.ActionType.ATRAN, worker=str(a.worker_id), payload="assigned")
        action.save()


def try_running_assign(assignment):
    max_createion_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=cfg.RUNNING_DELAY_MINUTES)

    room_candidates = list(Room.objects.all().filter(level__lte=cfg.MAX_RUNNIN_ASSIGN_LEVEL, finished=False, createion_time__gte=max_createion_time).order_by("createion_time"))
    logger.info("Try to add worker to running room. Room candidate count " + str(len(room_candidates)))
    for room in room_candidates:
        room_worker_count = len(list(WorkerAssignment.objects.all().filter(room_id = room.room_id)))
        if room_worker_count < cfg.MAX_ROOM_SIZE:
            assignment.room_id = room.room_id
            assignment.state = WorkerAssignment.AssignmentState.ASSIGNED
            logger.info("Set room " + str(room.room_id))
            action = ActionRecord(action_type=ActionRecord.ActionType.ATRAN, worker=str(assignment.worker_id), payload="assigned")
            action.save()
            return room.room_id
    return None



class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        try:
            assignments = list(WorkerAssignment.objects.all().filter(state=WorkerAssignment.AssignmentState.PENDING).order_by("created_at"))
        except WorkerAssignment.DoesNotExist:
            logger.info("No pending assignments")
            return
        logger.info("Found {} assignments".format(len(assignments)))

        dt = datetime.datetime.now(datetime.timezone.utc)

        updated_assignments = []
        rooms_to_notify = set()
        question_meta = QuestionMeta.objects.get(question_meta_id=cfg.DATASET)
        questions = list(Question.objects.all().filter(question_meta_id=question_meta).values_list('question_id', flat=True))

        for assignment_batch in batch(assignments, cfg.MAX_ROOM_SIZE):
            if len(assignment_batch) == cfg.MAX_ROOM_SIZE:
                create_room(assignment_batch, questions, question_meta)
                updated_assignments += assignment_batch
            elif len(assignment_batch) > 1 and max((dt - a.created_at).total_seconds() for a in assignment_batch) > (cfg.SOFT_TIMEOUT - len(assignment_batch) * 3 * 60):
                    logger.info("Worker waited to long")
                    create_room(assignment_batch, questions, question_meta)
                    updated_assignments += assignment_batch
            else:
                for a in assignment_batch:
                    if cfg.ALLOW_RUNNING_ASSIGN:
                        room = try_running_assign(a)
                        if room:
                            rooms_to_notify.add(room)
                            updated_assignments.append(a)
                    else:
                        seconds_passed = (dt - a.created_at).total_seconds()
                        if seconds_passed > cfg.HARD_TIMEOUT:
                            logger.info("Assignment of worker {} failed with timeout of {} seconds".format(assignment_batch[0].worker_id, seconds_passed))
                            a.state = WorkerAssignment.AssignmentState.FAILED
                            action = ActionRecord(action_type=ActionRecord.ActionType.ATRAN, worker=str(a.worker_id), payload="failed")
                            action.save()
                            updated_assignments.append(a)


        WorkerAssignment.objects.bulk_update(updated_assignments, ["room_id", "state"])

        channel_layer = get_channel_layer()

        for a in updated_assignments:
            logger.info("Sending new state to {}".format(a.worker_id))


            loop = asyncio.get_event_loop()
            coroutine = channel_layer.group_send(
                make_worker_group_name(a.worker_id),
                {
                    'type': 'state_update',
                    'assignment': model_to_dict(a)
                }
            )
            loop.run_until_complete(coroutine)

        # Force next question script

        all_rooms = Room.objects.all()
        current_time = datetime.datetime.now(datetime.timezone.utc)

        rooms_to_force = []
        for r in all_rooms:
            logger.info("Room {} spent {} seconds on same question".format(r.room_id, (current_time - r.last_activity_time).total_seconds()))
            if r.has_deadline and r.deadline_time < current_time:
                logger.info("Room {} is over time limit!".format(r.room_id))
                rooms_to_force.append(r.room_id)


        for r in rooms_to_force:
            with transaction.atomic():
                room = Room.objects.select_for_update().get(room_id=int(r))
                current_time = datetime.datetime.now(datetime.timezone.utc)
                if not room.has_deadline or room.deadline_time >= current_time:
                    continue

                room.last_activity_time = datetime.datetime.now(datetime.timezone.utc)
                try:
                    scores, quits = next_question(room=room)
                except:
                    continue
                room.save()
                loop = asyncio.get_event_loop()

                event = {"type": 'next'}
                if scores:
                    event['scores'] = scores if scores else None
                if quits:
                    event['quits'] = quits

                coroutine = channel_layer.group_send(
                    make_vote_group_name(room_id=room.room_id),
                    event
                )
                loop.run_until_complete(coroutine)

        for room in rooms_to_notify:
            event = {"type": 'renew'}
            coroutine = channel_layer.group_send(
                make_vote_group_name(room_id=room),
                event
            )
            loop.run_until_complete(coroutine)
