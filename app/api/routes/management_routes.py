from fastapi import APIRouter

router = APIRouter()

@router.get("/management/health/readiness")
async def readiness_status():
    from core.mongodb import get_database
    await get_database().command("ping")
    return {"status": "UP", "components": {"readinessState": {"status": "UP"}}}

@router.get("/management/health/liveness")
async def liveness_status():
    return {"status": "UP", "components": {"livenessState": {"status": "UP"}}}
