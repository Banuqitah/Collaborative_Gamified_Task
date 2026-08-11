from django.db import models as dj_models
from django.utils.translation import gettext_lazy as _


class Avatar(dj_models.Model):
    id = dj_models.AutoField(primary_key=True)
    path = dj_models.CharField(max_length=128)


class Mood(dj_models.Model):
    id = dj_models.AutoField(primary_key=True)
    path = dj_models.CharField(max_length=128)


class WorkerAssignment(dj_models.Model):
    class AssignmentState(dj_models.TextChoices):
        NEW = 'nw', _('new')
        PENDING = 'pd', _('pending')
        ASSIGNED = 'as', _('assigned')
        FAILED = 'fl', _('failed')
        DONE = 'dn', _('done')


    worker_id = dj_models.CharField(max_length=32, primary_key=True)
    room_id = dj_models.IntegerField(null=True)
    created_at = dj_models.DateTimeField(auto_now_add=True)
    state = dj_models.CharField(
        max_length=2, choices=AssignmentState.choices, default=AssignmentState.NEW,
    )
    score = dj_models.IntegerField(default=0)
    bonus_score = dj_models.IntegerField(default=0)
    login = dj_models.CharField(max_length=25, null=True, unique=True)
    avatar = dj_models.ForeignKey(Avatar, on_delete=dj_models.SET_NULL, null=True)
    mood = dj_models.ForeignKey(Mood, on_delete=dj_models.SET_NULL, null=True)
    assignment_id = dj_models.CharField(max_length=96, null=True)
    turk_submit_to = dj_models.CharField(max_length=40, null=True)
    createion_time = dj_models.DateTimeField(auto_now_add=True)
    quit_level = dj_models.IntegerField(default=-1)
    survey_code = dj_models.CharField(max_length=40, null=True)
    missed_questions = dj_models.IntegerField(default=0)
    quit_reason = dj_models.CharField(max_length=256, null=True)


class QuestionMeta(dj_models.Model):
    question_meta_id = dj_models.CharField(max_length=30, primary_key=True)
    answer_variants = dj_models.CharField(max_length=256)


class Question(dj_models.Model):
    question_id = dj_models.AutoField(primary_key=True)
    question_meta_id = dj_models.ForeignKey(QuestionMeta, on_delete=dj_models.CASCADE)
    question_text = dj_models.CharField(max_length=1024)
    question_image = dj_models.CharField(max_length=1024, default="", null=True)
    correct_answer = dj_models.IntegerField()


class QuestionSet(dj_models.Model):
    id = dj_models.AutoField(primary_key=True)
    question_meta_id = dj_models.ForeignKey(QuestionMeta, on_delete=dj_models.CASCADE)
    question_ids = dj_models.CharField(max_length=64)
    honeypot_indexes = dj_models.CharField(max_length=64)
    createion_time = dj_models.DateTimeField(auto_now_add=True)
    room_id = dj_models.IntegerField(default=0)
    level = dj_models.IntegerField(default=0)


class Room(dj_models.Model):
    room_id = dj_models.AutoField(primary_key=True)
    createion_time = dj_models.DateTimeField(auto_now_add=True)
    question_set = dj_models.ForeignKey(QuestionSet, on_delete=dj_models.CASCADE)
    question_set_progress = dj_models.IntegerField(default=0)
    last_activity_time = dj_models.DateTimeField(auto_now_add=True)
    score = dj_models.IntegerField(default=0)
    bonus_score = dj_models.IntegerField(default=0)

    level = dj_models.IntegerField(default=1)
    finished = dj_models.BooleanField(default=False)

    has_deadline = dj_models.BooleanField(default=False)
    deadline_time = dj_models.DateTimeField(auto_now_add=True)


class QuestionAnswerState(dj_models.Model):
    class Meta:
        unique_together = (('room', 'question'),)
    id = dj_models.AutoField(primary_key=True)
    room = dj_models.ForeignKey(Room, on_delete=dj_models.CASCADE)
    question = dj_models.ForeignKey(Question, on_delete=dj_models.CASCADE)
    state = dj_models.CharField(max_length=128, default="{}")
    submission_time = dj_models.DateTimeField(auto_now_add=True)
    createion_time = dj_models.DateTimeField(auto_now_add=True)


class ChatMessage(dj_models.Model):
    room = dj_models.ForeignKey(Room, on_delete=dj_models.CASCADE)
    worker = dj_models.ForeignKey(WorkerAssignment, on_delete=dj_models.CASCADE)
    text = dj_models.CharField(max_length=512)
    timestamp = dj_models.DateTimeField(auto_now_add=True)


class ActionRecord(dj_models.Model):
    class ActionType(dj_models.TextChoices):
        VOTE = 'vote', _('vote')
        LEND = 'lend', _('lend')
        ATRAN = 'atran', _('atran')
        ACTION = 'action', _('action')

    action_type = dj_models.CharField(max_length=8, choices=ActionType.choices)
    worker = dj_models.CharField(max_length=32)
    timestamp = dj_models.DateTimeField(auto_now_add=True)
    payload = dj_models.CharField(max_length=96)
