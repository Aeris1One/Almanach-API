#!/bin/bash

python celery_worker_prestart.py

celery -A app.tasks worker -l info -Q almanach -c 1 -B