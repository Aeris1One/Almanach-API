from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC


class FeedCreate(SQLModel, table=False):
    name: str
    slug: str


class Feed(FeedCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class FeedUpdate(SQLModel, table=True):
    feed_id: int = Field(foreign_key="feed.id", primary_key=True)
    date: datetime = Field(default=datetime.now(UTC), primary_key=True)
    state: str = Field(default="scheduled")
