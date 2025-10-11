from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
import uvicorn
from api.router_config import api_router
from core import mongodb
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
import asyncio
# Import webapp with fallback for missing dependencies
try:
    from webapp.webapp import app as webapp_app
    WEBAPP_AVAILABLE = True
    WEBAPP_MODE = "full"
except ImportError as e:
    print(f"Warning: Full webapp not available due to missing dependencies: {e}")
    print("Falling back to simple webapp...")
    try:
        from webapp.simple_webapp import app as webapp_app
        WEBAPP_AVAILABLE = True
        WEBAPP_MODE = "demo"
    except ImportError as e2:
        print(f"Error: Simple webapp also failed: {e2}")
        WEBAPP_AVAILABLE = False
        webapp_app = None
        WEBAPP_MODE = "none"

SERVER_PORT = int(os.getenv("SERVER_PORT", 5001))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application.")
    await mongodb.connect_mongodb()

    yield 

    await mongodb.disconnect_mongodb()
    logger.info("Stopping FastAPI application.")


app = FastAPI(lifespan=lifespan)


origins = [
    "*", # This configuration is intended for development purpose, it's **your** responsibility to harden it for production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Include webapp routes at root path (if available)
if WEBAPP_AVAILABLE and webapp_app:
    app.include_router(webapp_app.router, tags=["webapp"])
    logger.info(f"Webapp routes included at / (mode: {WEBAPP_MODE})")
else:
    logger.info("Webapp not available - missing dependencies")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=SERVER_PORT, reload=True)
