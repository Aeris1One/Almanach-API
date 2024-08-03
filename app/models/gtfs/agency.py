from typing import Optional
from sqlmodel import Field

from app.models.app.gtfs import AlmanachModel


class Agency(AlmanachModel, table=True):
    agency_id: Optional[str] = Field(default=None)
    agency_name: Optional[str] = Field(default=None)
    agency_url: Optional[str] = Field(default=None)
    agency_timezone: Optional[str] = Field(default=None)
    agency_lang: Optional[str] = Field(default=None)
    agency_phone: Optional[str] = Field(default=None)
    agency_fare_url: Optional[str] = Field(default=None)
    agency_email: Optional[str] = Field(default=None)
