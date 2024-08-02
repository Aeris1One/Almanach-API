FROM python:3.12-slim-bullseye

WORKDIR /backend

COPY ./requirements.txt /backend/requirements.txt

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r /backend/requirements.txt

COPY ./app /backend/app
COPY ./celery_worker_prestart.py /backend/celery_worker_prestart.py
COPY ./celery_start.sh /backend/celery_start.sh

CMD ["/backend/celery_start.sh"]