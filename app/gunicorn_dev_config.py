"""Gunicorn config file. [Development]

by WeDAA (https://www.wedaa.tech/)

# Gunicorn (v21) Configuration File
# Reference - https://docs.gunicorn.org/en/latest/settings.html
#
# To run gunicorn by using this config, run gunicorn by passing
# config file path, ex:
#
#       $ gunicorn -c=gunicorn_dev_config.py main:app
#
"""
import asyncio
from dotenv import load_dotenv
load_dotenv()
from core.mongodb import run_migrations

async def async_migration():
    """Run migrations asynchronously when the server is ready."""
    await run_migrations()

# ===============================================
#           Server Socket
# ===============================================

# bind - The server socket to bind
bind = "0.0.0.0:5001" 

# ===============================================
#           Worker Processes
# ===============================================
workers = 2 
worker_class = "uvicorn.workers.UvicornWorker"


# ===============================================
#           Debugging
# ===============================================

# reload - Restart workers when code changes
reload = True

# ===============================================
#           Logging
# ===============================================

# loglevel - The granularity of Error log outputs.
# Valid level names are:
    # 1. debug
    # 2. info
    # 3. warning
    # 4. error
    # 5. critical

loglevel = 'info'



# ===============================================
#           Server Hooks
# ===============================================

def on_starting(server):
    """
    Execute code just before the main process is initialized.
    """
    server.log.info("Running migrations...")
    asyncio.run(async_migration())
    server.log.info("Migrations completed.")

def when_ready(server):
    """
    Execute code just after the server is started.
    """
    server.log.info("Server is ready. Spawning workers")

def on_exit(server):
    """
    Execute code just before exiting gunicorn.
    """

