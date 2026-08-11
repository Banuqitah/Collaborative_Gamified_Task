from django.core.management.base import BaseCommand
from game.models import WorkerAssignment, Room, QuestionMeta, Avatar, Mood

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        WorkerAssignment.objects.all().delete()
        Room.objects.all().delete()
        QuestionMeta.objects.all().delete()
        Avatar.objects.all().delete()
        Mood.objects.all().delete()
