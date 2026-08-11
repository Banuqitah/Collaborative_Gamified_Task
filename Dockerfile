FROM nikolaik/python-nodejs:python3.12-nodejs24-bookworm

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN apt-get update && apt-get -y install cron

WORKDIR /collabel
COPY requirements.txt /collabel
RUN python -m pip install --upgrade pip -r requirements.txt
COPY collabel /collabel/collabel
COPY collabel_front /collabel/collabel_front
COPY game /collabel/game
COPY resource /collabel/resource
COPY static /collabel/static
COPY manage.py /collabel

COPY crontab /etc/cron.d/collabel_jobs
RUN chmod 0644 /etc/cron.d/collabel_jobs
RUN touch /var/log/cron.log

WORKDIR /collabel/collabel_front
RUN npm install
RUN npm run build
WORKDIR /collabel
ENV PYTHONPATH "${PYTHONPATH}:/collabel"

EXPOSE 8000
EXPOSE 8001
