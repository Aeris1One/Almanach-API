from sqlmodel import Session, select
import requests

from app.core.celery_app import celery_app
from app.core.config import settings

from app.core.db import engine
from app.models.app.feeds import Feed, FeedUpdate

from app.tasks.updater import updater

from datetime import datetime, UTC

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
    with Session(engine) as session:
        feeds = session.exec(select(Feed)).all()
        if feeds is None or len(feeds) == 0:
            return 'No feeds found, go add some more.'

        datasets = requests.get("https://transport.data.gouv.fr/api/datasets")
        datasets = datasets.json()
        if datasets is None:
            return 'No datasets available on transport.data.gouv.fr, weird.'

        for feed in feeds:
            dataset = next((dataset for dataset in datasets if dataset['slug'] == feed.slug), None)
            if dataset is None:
                # TODO: Send a warning if this happens
                continue
            dataset_last_modified = datetime.fromisoformat(dataset['updated'])
            feed_last_update = session.exec(select(FeedUpdate).where(FeedUpdate.feed_id == feed.id).order_by(FeedUpdate.date)).first()
            # Database doesn't store timezone info, but we're always using UTC
            feed_last_update = feed_last_update.date.replace(tzinfo=UTC) if feed_last_update is not None else None
            if feed_last_update is None or feed_last_update < dataset_last_modified:
                updater.delay(feed.id)
    return 'Scheduler done'

