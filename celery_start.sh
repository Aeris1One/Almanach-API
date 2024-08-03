#!/bin/bash

python celery_worker_prestart.py

if [ "$1" = 'worker' ]; then
    celery -A app.tasks worker -l info -Q scheduler,updater -c 1
elif [ "$1" = 'beat' ]; then
    celery -A app.tasks beat -l info
elif [ "$1" = 'flower' ]; then
    celery -A app.tasks flower
elif [ "$1" = 'local' ]; then
    # 'local' starts both the worker and the beat
    # useful for local development, shouldn't be used in production
    celery -A app.tasks worker -l info -Q scheduler,updater -c 1 -B
else
    echo "Unknown command"
    echo "Commands: worker, beat, flower, local"
    exit 1
fi