from fastapi import APIRouter
from sqlmodel import Session

from app.models.gtfs.agency import Agency
from app.core.db import engine

router = APIRouter()


@router.get("/create")
async def create_agency(internal_id: str, agency_id: str, agency_name: str):
    with Session(engine) as session:
        agency = Agency(internal_id=internal_id, agency_id=agency_id, agency_name=agency_name)
        session.add(agency)
        session.commit()
        session.refresh(agency)

    return agency


@router.get("/get", response_model=Agency)
async def get_agency(internal_id: str):
    with Session(engine) as session:
        agency = session.get(Agency, internal_id)
    return agency
