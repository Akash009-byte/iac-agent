"""Gunicorn config file. [Production]

by WeDAA (https://www.wedaa.tech/)

# Gunicorn (v21) Configuration File
# Reference - https://docs.gunicorn.org/en/latest/settings.html
#
# To run gunicorn by using this config, run gunicorn by passing
# config file path, ex:
#
#       $ gunicorn -c=gunicorn_prod_config.py main:app
#
"""
import multiprocessing
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

# workers - The number of worker processes for handling requests.
# A positive integer generally in the 2-4 x $(NUM_CORES) range
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

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
#           Security
# ===============================================

# limit_request_line - The maximum size of HTTP request line in bytes
# Value is a number from 0 (unlimited) to 8190.
# This parameter can be used to prevent any DDOS attack.
limit_request_line = 1024

# limit_request_fields - Limit the number of HTTP headers fields in a request
# This parameter is used to limit the number of headers in a request to
# prevent DDOS attack. Used with the limit_request_field_size it allows
# more safety.
# By default this value is 100 and can’t be larger than 32768.
limit_request_fields = 100

# limit_request_field_size - Limit the allowed size of an HTTP request
# header field.
# Value is a number from 0 (unlimited) to 8190.
limit_request_field_size = 1024


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

