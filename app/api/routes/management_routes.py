from fastapi import APIRouter

router = APIRouter()

@router.get("/management/health/readiness")
async def readiness_status():
    return {"status": "UP", "components": {"readinessState": {"status": "UP"}}}

@router.get("/management/health/liveness")
async def liveness_status():
    return {"status": "UP", "components": {"livenessState": {"status": "UP"}}}
