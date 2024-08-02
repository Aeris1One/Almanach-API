import random

from app.core.celery_app import celery_app
from app.core.config import settings

from app.tasks.updater import updater

@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(15, scheduler.s(), name='scheduler')


@celery_app.task()
def scheduler():
    """
    A periodic task that runs every 15 minutes.
    It checks, using the transport.data.gouv.fr API, if the data stored in the database is up to date.
    If not, it schedules an 'updater' task to update the data. Hence the 'scheduler' name.
    """
    for i in range(random.randint(1, 5)):
        n = random.randint(1, 500)
        print(f"Scheduling updater for feed {n}")
        updater.delay(n)
    return 'Scheduler done'
