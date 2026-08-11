import datetime
import json

from django.db import transaction
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import QuestionAnswerState, Room, ChatMessage, WorkerAssignment, ActionRecord
from .settings import MAX_ROOM_SIZE, DEADLINE_TIME
from .score import next_question
import logging

logger = logging.getLogger(__name__)


def make_worker_group_name(worker_id):
    return 'worker_%s' % worker_id


def make_vote_group_name(room_id):
    return 'room_vote_%s' % room_id


class WorkerStateConsumer(WebsocketConsumer):
    def connect(self):
        self.worker_id = self.scope['url_route']['kwargs']['worker_id']
        self.worker_group_name = make_worker_group_name(self.worker_id)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.worker_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.worker_group_name,
            self.channel_name
        )

    # Receive message from room group
    def state_update(self, event):
        message = event['assignment']
        self.send(text_data=json.dumps(message))


class VoteConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.vote_group_name = 'room_vote_%s' % self.room_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.vote_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.vote_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        logger.info(text_data)
        if "quit" in text_data:
            _, worker, quit_reason = json.loads(text_data)

            room = Room.objects.get(room_id=int(self.room_id))
            with transaction.atomic():
                w = WorkerAssignment.objects.get(worker_id=worker)
                w.state = WorkerAssignment.AssignmentState.DONE
                w.quit_level = room.level
                w.quit_reason = quit_reason
                logger.info("Worker {} quits. Level {}".format(worker, w.quit_level))
                w.save()
                action = ActionRecord(action_type=ActionRecord.ActionType.ACTION, worker=str(w.worker_id), payload="quit")
                action.save()
            async_to_sync(self.channel_layer.group_send)(
                self.vote_group_name,
                {
                    'type': 'quit'
                }
            )
            return

        room = Room.objects.select_for_update().get(room_id=int(self.room_id))
        room.last_activity_time = datetime.datetime.now(datetime.timezone.utc)
        room.save()

        worker, question, answer, checked = json.loads(text_data)
        logger.info("Received {} {} {} {}".format(worker, question, answer, checked))

        advance = False
        scores = {}

        with transaction.atomic():
            room = Room.objects.select_for_update().get(room_id=int(self.room_id))
            room.last_activity_time = datetime.datetime.now(datetime.timezone.utc)

            question_id = [int(v) for v in room.question_set.question_ids.split(",")][room.question_set_progress]
            if question_id != question:
                return

            state_obj = QuestionAnswerState.objects.select_for_update().get(room_id=int(self.room_id), question_id=question)

            state = json.loads(state_obj.state)
            if len(state.values()) == MAX_ROOM_SIZE and all(v[1] for v in state.values()):
                logger.info("Question already confirmed!")
                async_to_sync(self.channel_layer.group_send)(
                    self.vote_group_name,
                    {
                        'type': 'next'
                    }
                )

            state[worker] = (answer, checked)
            state_obj.state = json.dumps(state)
            state_obj.submission_time = datetime.datetime.now(datetime.timezone.utc)
            state_obj.save()

            action = ActionRecord(action_type=ActionRecord.ActionType.VOTE, worker=worker, payload=json.dumps({
                "vote": answer,
                "submit": checked,
                "answer_id": state_obj.id
            }))
            action.save()

            workers = list(WorkerAssignment.objects.all().filter(room_id=room.room_id).filter(state=WorkerAssignment.AssignmentState.ASSIGNED))
            if sum(v[1] for v in state.values()) >= (len(workers) // 2 + (len(workers) % 2)) and not room.has_deadline:
                room.has_deadline = True
                room.deadline_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=DEADLINE_TIME)

            filtered_state = {w.worker_id: state[w.worker_id] for w in workers if w.worker_id in state}

            if len(filtered_state.values()) == len(workers) and all(v[1] for v in filtered_state.values()):
                scores, quits = next_question(room=room)
                advance = True
                logger.info("advance")

            room.save()

        if advance:
            event = {"type": 'next'}
            if scores:
                event['scores'] = scores
            if quits:
                event['quits'] = list(quits)
            async_to_sync(self.channel_layer.group_send)(self.vote_group_name, event)
        else:
            logger.info("Resending votes to group")
            async_to_sync(self.channel_layer.group_send)(
            self.vote_group_name,
            {
                'type': 'vote',
                'vote': [worker, question, answer, checked],
                'has_deadline': room.has_deadline,
                'deadline': room.deadline_time.timestamp() * 1000
            }
        )

    def vote(self, event):
        self.send(text_data=json.dumps({"vote": event['vote'], "deadline": event['deadline'], "has_deadline": event['has_deadline']}))

    def next(self, event):
        self.send(text_data=json.dumps({"next": True, "scores": event["scores"] if "scores" in event else None, "quits": event["quits"] if "quits" in event else None}))

    def quit(self, event):
        self.send(text_data=json.dumps({"quit": True}))

    def renew(self, event):
        self.send(text_data=json.dumps({"renew": True}))


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group_name = 'room_chat_%s' % self.room_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        room = Room.objects.select_for_update().get(room_id=int(self.room_id))
        room.last_activity_time = datetime.datetime.now(datetime.timezone.utc)
        room.save()

        worker, message_text = json.loads(text_data)
        msg = ChatMessage(room_id=self.room_id, worker_id=worker, text=message_text)
        msg.save()

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'msg',
                'data': json.loads(text_data)
            }
        )

    def msg(self, event):
        self.send(text_data=json.dumps({"data": event["data"]}))
