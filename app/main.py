from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from api.router_config import api_router
from core import mongodb
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
import asyncio
from pathlib import Path

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

# Chainlit removed - using custom HTML UI
CHAINLIT_AVAILABLE = False

SERVER_PORT = int(os.getenv("SERVER_PORT", 5001))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application.")

    # Try to connect to MongoDB, but don't fail startup if it fails
    try:
        await mongodb.connect_mongodb()
        logger.info("MongoDB connection successful.")
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Application will continue without database.")

    yield

    # Try to disconnect from MongoDB
    try:
        await mongodb.disconnect_mongodb()
        logger.info("MongoDB disconnected.")
    except Exception as e:
        logger.warning(f"MongoDB disconnect failed: {e}")

    logger.info("Stopping FastAPI application.")


app = FastAPI(lifespan=lifespan)

from bson.errors import InvalidId
from fastapi.responses import JSONResponse

@app.exception_handler(InvalidId)
async def invalid_id_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": "Invalid resource ID"})



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

# Add WebSocket CORS middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles
# Mount static files
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

class WebSocketCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/ws/") or request.url.path.startswith("/webapp/ws/"):
            # Allow WebSocket connections from any origin
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response
        return await call_next(request)

app.add_middleware(WebSocketCORSMiddleware)

app.include_router(api_router)

# Add EC2Forge Homepage route FIRST (takes precedence)
@app.get("/", response_class=HTMLResponse)
async def ec2forge_homepage():
    """Serve EC2Forge Homepage"""
    html_file = Path(__file__).parent / "webapp" / "templates" / "index.html"
    if html_file.exists():
        with open(html_file, 'r') as f:
            return HTMLResponse(content=f.read(), status_code=200)
    else:
        return HTMLResponse(content="EC2Forge Homepage not found", status_code=404)

# Include webapp routes at /webapp path (if available)
if WEBAPP_AVAILABLE and webapp_app:
    if WEBAPP_MODE == "full":
        # For full webapp, include router
        app.include_router(webapp_app.router, prefix="/webapp", tags=["webapp"])

        # Add WebSocket route at root level for backward compatibility
        try:
            from webapp.webapp import websocket_endpoint
            from fastapi import WebSocket

            @app.websocket("/ws/{user_id}")
            async def root_websocket_endpoint(websocket: WebSocket, user_id: str):
                """WebSocket endpoint at root level for backward compatibility"""
                await websocket_endpoint(websocket, user_id)

            logger.info("WebSocket routes added at both /webapp/ws/ and /ws/ for compatibility")
        except ImportError as e:
            logger.warning(f"Could not import full webapp WebSocket endpoint: {e}")

        logger.info(f"Webapp router included at /webapp (mode: {WEBAPP_MODE})")
    else:
        # For simple webapp, include its routes directly with /webapp prefix
        from fastapi import Request
        from fastapi.responses import HTMLResponse
        from fastapi.templating import Jinja2Templates
        import os

        # Set up templates for simple webapp routes
        templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "webapp", "templates"))

        @app.get("/webapp/", response_class=HTMLResponse)
        async def webapp_home(request: Request):
            """Serve the webapp home page"""
            return templates.TemplateResponse(request=request, name="chat.html", context={})

        @app.get("/webapp/activity-log")
        @app.get("/webapp/activity-log/")
        @app.get("/webapp/activity_log")
        @app.get("/webapp/activity_log/")
        @app.get("/activity-log")
        @app.get("/activity-log/")
        @app.get("/activity_log")
        @app.get("/activity_log/")
        async def webapp_activity_log(request: Request):
            """Serve the activity log page"""
            return templates.TemplateResponse(request=request, name="activity_log.html", context={})

        @app.get("/webapp/health")
        async def webapp_health():
            """Health check endpoint for webapp"""
            from datetime import datetime
            return {"status": "healthy", "timestamp": datetime.now().isoformat(), "mode": "demo"}

        logger.info(f"Simple webapp routes included at /webapp (mode: {WEBAPP_MODE})")
else:
    logger.info("Webapp not available - missing dependencies")

# Add EC2Forge UI information endpoint
@app.get("/ec2forge-ui")
async def ec2forge_ui_info():
    """Information about EC2Forge UI"""
    return {
        "available": True,
        "url": f"http://localhost:{SERVER_PORT}/",
        "port": SERVER_PORT,
        "description": "EC2Forge - Instant AWS Instances UI",
        "features": [
            "AI-Powered Automation",
            "Templates & Blueprints",
            "Real-time Monitoring",
            "Visual Operation Progress"
        ]
    }

if __name__ == "__main__":
    print("=" * 60)
    print("🌩️ EC2Forge - Instant AWS Instances")
    print("   Streamline Your AWS EC2 Provisioning")
    print("=" * 60)
    print(f"🚀 Starting FastAPI server on port {SERVER_PORT}")
    print(f"🎨 EC2Forge Homepage available at: http://localhost:{SERVER_PORT}/")
    print("📊 API docs available at: http://localhost:{}/docs".format(SERVER_PORT))
    print("🔍 EC2Forge UI info: http://localhost:{}/ec2forge-ui".format(SERVER_PORT))
    print("=" * 60)

    uvicorn.run("main:app", host="0.0.0.0", port=SERVER_PORT, reload=True)


@app.get("/integrations/status")
async def integration_status():
    return {"openai": bool(os.getenv("OPENAI_API_KEY")), "aws": bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))}
