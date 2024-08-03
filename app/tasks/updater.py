from sqlmodel import Session

from app.core.celery_app import celery_app
from app.core.config import settings

from app.core.db import engine
from app.models.app.feeds import Feed, FeedUpdate


@celery_app.task()
def updater(feed_id: int):
    """
    A task that updates the data stored in the database.
    """
    with Session(engine) as session:
        feed = session.get(Feed, feed_id)
        if feed is None:
            return 'Feed not found'
        session.add(FeedUpdate(feed_id=feed_id))
        session.commit()
    return 'Updater done'
