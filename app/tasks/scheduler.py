from sqlmodel import Session, select, desc
import requests
from celery.app.control import Inspect

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
            # If there is already a scheduled update for this feed, skip it
            feed_update = session.exec(select(FeedUpdate).where(FeedUpdate.feed_id == feed.id).where(FeedUpdate.state == 'scheduled')).first()
            if feed_update is not None:
                print(f"Feed {feed.id} already has an update scheduled, skipping.")
                continue

            dataset = next((dataset for dataset in datasets if dataset['slug'] == feed.slug), None)
            if dataset is None:
                # TODO: Send a warning if this happens
                continue
            dataset_last_modified = datetime.fromisoformat(dataset['updated'])

            feed_update = session.exec(select(FeedUpdate).where(FeedUpdate.feed_id == feed.id).where(FeedUpdate.state == 'done').order_by(desc(FeedUpdate.date)).limit(1)).first()
            print(f"Feed {feed.id} last updated on {feed_update.date if feed_update is not None else 'never'}, dataset last modified on {dataset_last_modified}")
            if feed_update is None or feed_update.date.replace(tzinfo=UTC) < dataset_last_modified:
                update_time = datetime.now()
                updater.delay(feed.id, update_time)
                session.add(FeedUpdate(feed_id=feed.id, date=update_time, state='scheduled'))
                session.commit()
    return 'Scheduler done'

