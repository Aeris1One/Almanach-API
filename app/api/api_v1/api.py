from fastapi import APIRouter

from app.api.api_v1.endpoints import template, agency, admin

api_router = APIRouter()
api_router.include_router(template.router, prefix="/template", tags=["temp"])
api_router.include_router(agency.router, prefix="/agency", tags=["create"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])