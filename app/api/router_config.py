from fastapi import APIRouter
from api.routes import (
    management_routes,
    common_routes,
    note_routes
)

api_router = APIRouter()

api_router.include_router(management_routes.router, tags=["management-endpoints"])
api_router.include_router(common_routes.router, tags=["common-endpoints"])
api_router.include_router(note_routes.router, tags=["note-endpoints"])
