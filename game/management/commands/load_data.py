import os

import simplejson as json
from django.core.management.base import BaseCommand
from game.models import QuestionMeta, Question, Avatar, Mood
from game.settings import DATASET

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        logger.info("Avatar count: {}".format(len(list(Avatar.objects.all()))))

        if len(list(Avatar.objects.all())) > 0:
            logger.info("Database not empty. Skipping.")
            return

        meta = QuestionMeta(
            question_meta_id=DATASET,
            answer_variants="1,2,3,4,more than 4,cant tell"
        )

        meta.save()

        ans_to_id = {
            v: i for i, v in enumerate("1,2,3,4,more than 4,cant tell".split(","))
        }

        lines = open("resource/datasets/galaxy/galaxies.json", "r")
        data = json.load(lines)
        objs = []
        for o in data:
            objs.append(
                Question(
                    question_meta_id=meta,
                    correct_answer=ans_to_id[o["label"]],
                    question_text="How many spiral arms are there?",
                    question_image="/static/galaxy/{}.jpg".format(o["img"])
                    )
                )

        Question.objects.bulk_create(objs)
        logger.info("Loaded {} questions".format(len(objs)))

        avatar_objs = []
        for file in os.listdir("static/avatars"):
            avatar_objs.append(Avatar(path="/static/avatars/" + file))
        Avatar.objects.bulk_create(avatar_objs)
        logger.info("Loaded {} avatars".format(len(avatar_objs)))

        mood_objs = []
        for file in os.listdir("static/mood"):
            if file.endswith(".png"):
                mood_objs.append(Mood(path="/static/mood/" + file))
        Mood.objects.bulk_create(mood_objs)
        logger.info("Loaded {} moods".format(len(mood_objs)))
