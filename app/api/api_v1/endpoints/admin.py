from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlmodel import Session, select
from typing import List, Annotated, Union

from app.core.config import settings
from app.models.app.feeds import Feed, FeedCreate, FeedUpdate
from app.core.db import engine

router = APIRouter()

auth_scheme = APIKeyHeader(name="Authorization")


def check_token(token: str = Depends(auth_scheme)):
    if token == settings.ADMIN_API_KEY:
        return
    raise HTTPException(status_code=403, detail="Invalid API Key")


@router.get("/feeds", response_model=List[Feed])
async def get_feeds():
    """
    Get all feeds this server is configured to serve.
    """
    with Session(engine) as session:
        feeds = session.exec(select(Feed)).all()
    return feeds


@router.get("/feeds/{feed_id}", response_model=Feed)
async def get_feed(feed_id: int):
    """
    Get a specific feed by ID.
    """
    with Session(engine) as session:
        feed = session.get(Feed, feed_id)
        if feed is None:
            raise HTTPException(status_code=404, detail="Feed not found")
    return feed


@router.post("/feeds", response_model=Feed, dependencies=[Depends(check_token)])
async def create_feed(feed: FeedCreate):
    """
    Create a new feed.
    """
    with Session(engine) as session:
        feed = Feed.model_validate(feed)
        session.add(feed)
        session.commit()
        session.refresh(feed)
    return feed


@router.put("/feeds/{feed_id}", response_model=Feed, dependencies=[Depends(check_token)])
async def update_feed(feed_id: int, feed: FeedCreate):
    """
    Update an existing feed.
    """
    with Session(engine) as session:
        feed = session.get(Feed, feed_id)
        if feed is None:
            raise HTTPException(status_code=404, detail="Feed not found")
        feed.name = feed.name
        feed.slug = feed.slug
        session.add(feed)
        session.commit()
        session.refresh(feed)
    return feed


@router.delete("/feeds/{feed_id}", dependencies=[Depends(check_token)])
async def delete_feed(feed_id: int):
    """
    Delete a feed.
    """
    with Session(engine) as session:
        feedupdates = session.exec(select(FeedUpdate).where(FeedUpdate.feed_id == feed_id)).all()
        for feedupdate in feedupdates:
            session.delete(feedupdate)
        feed = session.get(Feed, feed_id)
        if feed is None:
            raise HTTPException(status_code=404, detail="Feed not found")
        session.delete(feed)
        session.commit()
    return {"message": "Feed deleted"}