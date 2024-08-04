from typing import Optional
from sqlmodel import Field, SQLModel


class AlmanachModel(SQLModel, table=False):
    internal_id: int = Field(default=None, foreign_key="feed.id", primary_key=True)