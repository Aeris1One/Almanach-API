from app.core.celery_app import celery_app

from app.tasks.scheduler import scheduler
from app.tasks.updater import updater