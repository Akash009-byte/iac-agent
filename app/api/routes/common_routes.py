from fastapi import APIRouter
from services.app_details import fetch_app_details

router = APIRouter()


@router.get(
    "/api/services/agent",
)
def get_app_details():
    app_details = fetch_app_details()
    return app_details


