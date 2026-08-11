import datetime
import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt

from . import models
from .settings import get_set_params
import os

import logging
logger = logging.getLogger(__name__)


def get_room_state_dict(room_id):
    room = models.Room.objects.get(room_id=room_id)
    question_id = [int(v) for v in room.question_set.question_ids.split(",")][room.question_set_progress]
    question = models.Question.objects.get(question_id=question_id)
    workers = models.WorkerAssignment.objects.all().filter(room_id=room_id).filter(state=models.WorkerAssignment.AssignmentState.ASSIGNED)
    answer_state = json.loads(models.QuestionAnswerState.objects.select_for_update().get(room_id=int(room_id), question_id=question_id).state)

    chat_messages = models.ChatMessage.objects.all().filter(room_id=room_id).order_by("timestamp")
    chat_json = [(msg.worker_id, msg.text) for msg in chat_messages]

    leader_board = [
        {"id": r.room_id, "score": r.score, "bonus_score": r.bonus_score} for r in models.Room.objects.all().order_by("score")
    ][::-1]

    for i, t in enumerate(leader_board):
        if t["id"] == room.room_id:
            break
    
    low_idx = max(i-2, 0)
    leader_board = leader_board[low_idx : i + 2]

    set_params = get_set_params(room.level)

    return {
        "id": room.room_id,
        "logins": {w.worker_id: w.login for w in workers},
        "avatars": {w.worker_id: w.avatar.path for w in workers},
        "scores": {
            w.worker_id: w.score for w in workers
        },
        "room_score": room.score,
        "room_bonus_score": room.bonus_score,
        "progress": room.question_set_progress + 1,
        "level": room.level,
        "q_set_size": set_params.normals + set_params.honeypots,
        "q": {
            "id": question.question_id,
            "text": question.question_text,
            "img": question.question_image,
            "answers": room.question_set.question_meta_id.answer_variants.split(","),
        },
        "votes": answer_state,
        "chat": chat_json,
        "lb": leader_board,
        "finished": room.finished,

        "deadline": (room.deadline_time.timestamp()) * 1000,
        "has_deadline": room.has_deadline
    }

@xframe_options_exempt
def index(request):
    assignment_id = request.GET.get("assignmentId", None)
    submit_to = request.GET.get("turkSubmitTo", None)

    if assignment_id == "ASSIGNMENT_ID_NOT_AVAILABLE":
        return render(request, 'game/index.html', context={
            "state": {
                "worker_id": "preview_worker",
                "assignment": {"state": "pr"},
                "room_id": None,
                "has_code": False,
                "mode": os.getenv("GAME_MODE", default="normal")
            },
        })

    worker_id = request.GET.get("workerId", None)
    if not worker_id:
        return HttpResponse("Set workerId in url")


    try:
        assignment = models.WorkerAssignment.objects.get(worker_id=worker_id)
    except models.WorkerAssignment.DoesNotExist:
        assignment = models.WorkerAssignment(worker_id=worker_id, assignment_id=assignment_id, turk_submit_to=submit_to)
        assignment.save()

    room_id = None

    if assignment.state == models.WorkerAssignment.AssignmentState.ASSIGNED:
        room_id = assignment.room_id
    if assignment.state == models.WorkerAssignment.AssignmentState.FAILED:
        assignment.state = models.WorkerAssignment.AssignmentState.PENDING
        assignment.created_at = datetime.datetime.now()
        assignment.save()

    return render(request, 'game/index.html', context={
        "state": {
            "worker_id": worker_id,
            "assignment": model_to_dict(assignment),
            "room_id": room_id,
            "has_code": assignment.survey_code is not None,
            "score": assignment.score,
            "submit_url": assignment.turk_submit_to,
            "assignment_id": assignment.assignment_id,
            "mode": os.getenv("GAME_MODE", default="normal")
        }
    })


def room_state(request, room_id):
    return JsonResponse(get_room_state_dict(room_id))


@csrf_exempt
def set_login(request, worker_id):
    if request.method == "POST":
        parsed_content = json.loads(request.body)
        new_login = parsed_content["login"]
        avatar = parsed_content["avatar"]
        mood = parsed_content["mood"]
        with transaction.atomic():
            w = models.WorkerAssignment.objects.get(worker_id=worker_id)
            w.login = new_login
            w.avatar = models.Avatar(id=avatar)
            w.mood = models.Mood(id=mood)
            w.state = models.WorkerAssignment.AssignmentState.PENDING

            action = models.ActionRecord(action_type=models.ActionRecord.ActionType.ATRAN, worker=str(worker_id), payload="pending")
            action.save()

            try:
                w.save()
            except IntegrityError:
                return JsonResponse({"result": "Error", "code": 1})
            return JsonResponse({"result": "Ok"})


@csrf_exempt
def set_survey(request, worker_id):
    if request.method == "POST":
        parsed_content = json.loads(request.body)
        code = parsed_content["code"]
        with transaction.atomic():
            w = models.WorkerAssignment.objects.get(worker_id=worker_id)
            w.survey_code = code
            try:
                w.save()
            except IntegrityError:
                return JsonResponse({"result": "Error", "code": 1})
            return JsonResponse({"result": "Ok"})


@csrf_exempt
def send_action(request, worker_id):
    if request.method == "POST":
        parsed_content = json.loads(request.body)
        action = parsed_content["action"]
        action = models.ActionRecord(action_type=models.ActionRecord.ActionType.ACTION, worker=str(worker_id), payload=action)
        action.save()
        return JsonResponse({"result": "Ok"})


def list_avatars(request):
    avatars = models.Avatar.objects.all()
    moods = models.Mood.objects.all()
    return JsonResponse({
        "av": [(a.id, a.path) for a in avatars],
        "md": sorted([(m.id, m.path) for m in moods if m.path.endswith(".png")], key= lambda x: x[1])
    })


def get_pending(request):
    pending_count = len(models.WorkerAssignment.objects.all().filter(state=models.WorkerAssignment.AssignmentState.PENDING))
    return JsonResponse({
        "panding_count": pending_count,
    })