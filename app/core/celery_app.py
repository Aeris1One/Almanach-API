from celery import Celery
from app.core.config import settings

celery_app = Celery('core', broker=str(settings.BROKER_DSN))

celery_app.conf.task_routes = {
    'app.tasks.*': {'queue': 'almanach'},
}
