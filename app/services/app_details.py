import os
from core.log_config import logger

APP_NAME = os.getenv("APP_NAME")

def fetch_app_details():
    logger.info("Generating application details")
    app_details = {
        "status": "running", 
        "server": APP_NAME
    }
    return app_details
    