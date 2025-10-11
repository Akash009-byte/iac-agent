from fastapi import APIRouter
from api.routes import (
    management_routes,
    common_routes,
    note_routes
)
from gmail.routes import router as gmail_router

api_router = APIRouter()

api_router.include_router(management_routes.router, tags=["management-endpoints"])
api_router.include_router(common_routes.router, tags=["common-endpoints"])
api_router.include_router(note_routes.router, tags=["note-endpoints"])
api_router.include_router(gmail_router, prefix="/gmail", tags=["gmail-endpoints"])
