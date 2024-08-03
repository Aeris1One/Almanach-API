from typing import Optional
from sqlmodel import Field, SQLModel


class AlmanachModel(SQLModel, table=False):
    internal_id: Optional[str] = Field(default=None, primary_key=True)