import sys

TEMPLATES = [
    {
        # Template backend to be used, For example Jinja
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Directories for templates
        'DIRS': [],
        'APP_DIRS': True,

        # options to configure
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MAX_ROOM_SIZE = 5
MAX_LEVEL = 5
SOFT_TIMEOUT = 15 * 60
HARD_TIMEOUT = 16 * 60

ALLOW_RUNNING_ASSIGN = True
MAX_RUNNIN_ASSIGN_LEVEL = 1
RUNNING_DELAY_MINUTES = 4

AUTOQUIT_LIMIT = 4

DATASET = ["sarcasm_headlines"]
DEADLINE_TIME = 60
SURVEY_LINK = "https://strathsci.qualtrics.com/jfe/form/SV_0HAgacQVTuD9Ip0"

CONVERSION_RATE = 0.01

class QuestionSetParams:
    def __init__(self, normals, honeypots, base_score, majority_score, agreement_score, accuracy_score):
        self.normals = normals
        self.honeypots = honeypots
        self.base_score = base_score
        self.majority_score = majority_score
        self.agreement_score = agreement_score
        self.accuracy_score = accuracy_score

    @property
    def question_count(self):
        return self.normals + self.honeypots

    @property
    def total_base_score(self):
        return self.base_score * self.question_count

    @property
    def total_bonus_score(self):
        return self.agreement_score * self.question_count + self.honeypots * self.accuracy_score

    @property
    def total_score(self):
        return self.total_base_score + self.total_bonus_score


HARDCODED_PARAMS = [
    QuestionSetParams(normals=9, honeypots=1, base_score=5, majority_score=1, agreement_score=3, accuracy_score=25),
    QuestionSetParams(normals=9, honeypots=1, base_score=5, majority_score=1, agreement_score=3, accuracy_score=30),
    QuestionSetParams(normals=9, honeypots=1, base_score=5, majority_score=1, agreement_score=3, accuracy_score=35),
    QuestionSetParams(normals=9, honeypots=1, base_score=5, majority_score=1, agreement_score=3, accuracy_score=40),
    QuestionSetParams(normals=9, honeypots=1, base_score=5, majority_score=1, agreement_score=3, accuracy_score=45),
]

game_score = sum(s.total_score for s in HARDCODED_PARAMS)
print("Total score:", game_score, file=sys.stderr)

def get_set_params(level):
    level = level - 1
    if level < len(HARDCODED_PARAMS):
        return HARDCODED_PARAMS[level]
    return HARDCODED_PARAMS[-1]
