#!/bin/bash

python celery_worker_prestart.py

celery -A app.worker worker -l info -Q almanach -c 1