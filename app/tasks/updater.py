from app.core.celery_app import celery_app
from app.core.config import settings


@celery_app.task()
def updater(feed_id: int):
    """
    A task that updates the data stored in the database.
    """
    print(f"Updating feed {feed_id}")
    return 'Update done'