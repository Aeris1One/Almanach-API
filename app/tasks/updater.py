import os

from sqlmodel import Session, delete, select
import requests
from datetime import datetime
import tempfile
import zipfile
import csv

from app.core.celery_app import celery_app
from app.core.config import settings

from app.core.db import engine
from app.models.app.feeds import Feed, FeedUpdate
from app.models.gtfs.agency import Agency


@celery_app.task()
def updater(feed_id: int, update_time: datetime):
    """
    A task that updates the data stored in the database.
    """

    def mark_as_failed(feed_id: int, update_time: datetime, message: str = None):
        try:
            with Session(engine) as session:
                feedupdate = session.get(FeedUpdate, (feed_id, update_time))

                feedupdate.state = 'failed'
                session.commit()
                if message:
                    return Exception(f'Updater failed: {message}')
        except Exception as e:
            return Exception('Updater failed and was unable to mark as failed on the database : {e}')

    def mark_as_done(feed_id: int, update_time: datetime):
        try:
            with Session(engine) as session:
                feedupdate = session.get(FeedUpdate, (feed_id, update_time))
    
                feedupdate.state = 'done'
                session.commit()
                return 'Updater done'
        except Exception as e:
            raise Exception('Updater done but was unable to mark as done on the database : {e}')
            
    with Session(engine) as session:
        # ---
        # Setup
        # ---
        feedupdate = session.get(FeedUpdate, (feed_id, update_time))
        if feedupdate is None:
            raise mark_as_failed(feed_id, update_time, message='FeedUpdate not found')

        feed = session.get(Feed, feed_id)
        if feed is None:
            raise mark_as_failed(feed_id, update_time, message='Feed not found')

        # Retrieve feed information from the API
        datasets = requests.get("https://transport.data.gouv.fr/api/datasets")
        datasets = datasets.json()
        if datasets is None:
            raise mark_as_failed(feed_id, update_time,
                                  message='No datasets available on transport.data.gouv.fr, weird.')

        dataset = next((dataset for dataset in datasets if dataset['slug'] == feed.slug), None)
        if dataset is None:
            raise mark_as_failed(feed_id, update_time, message='Dataset not found')

        # Retrieve the resource which has a "format"="GTFS" and "community_resource_publisher" is not set
        resource = next((resource for resource in dataset['resources'] if
                         resource['format'] == 'GTFS' and 'community_resource_publisher' not in resource), None)
        if resource is None:
            raise mark_as_failed(feed_id, update_time, message='Resource not found')

        # ---
        # Remove old data
        # ---
        session.exec(delete(Agency).where(Agency.internal_id == feed_id))

        # ---
        # Update with new data
        # ---

        with tempfile.TemporaryDirectory() as tempdir:
            # DOWNLOAD
            try:
                gtfs = requests.get(resource['url'])
                with open(f"{tempdir}/gtfs.zip", "wb") as f:
                    f.write(gtfs.content)
            except Exception as e:
                raise mark_as_failed(feed_id, update_time, message=f'Unable to download GTFS feed: {e}')

            # UNZIP
            try:
                with zipfile.ZipFile(f"{tempdir}/gtfs.zip", 'r') as zip_ref:
                    zip_ref.extractall(f"{tempdir}/gtfs")
            except Exception as e:
                raise mark_as_failed(feed_id, update_time, message=f'Unable to unzip GTFS feed: {e}')

            # UPLOAD
            try:
                # agencies.txt
                with open(f"{tempdir}/gtfs/agency.txt", "r", encoding='utf-8-sig') as f:
                    csvreader = list(csv.DictReader(f))
                    for row in csvreader:
                        if row['agency_id'] == '':
                            row['agency_id'] = feed.slug
                        row['internal_id'] = feed_id
                        agency = Agency.model_validate(row)
                        session.add(agency)

            except Exception as e:
                raise mark_as_failed(feed_id, update_time, message=f'Unable to parse GTFS feed: {e}')

        session.commit()

    return mark_as_done(feed_id, update_time)
