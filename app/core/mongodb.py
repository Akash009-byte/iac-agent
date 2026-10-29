import os
import motor.motor_asyncio
from core.log_config import logger
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from mongo_migrate.migration_manager import MigrationManager
from mongo_migrate.exceptions import MongoMigrateException
from types import SimpleNamespace

# Initialize global variables
client = None
database = None

# Type alias for PyObjectId using Annotated
PyObjectId = Annotated[str, BeforeValidator(str)]

def get_database():
    """Return the connected database."""
    if database is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database is unavailable")
    return database

async def run_migrations():
    """Run database migrations using mongo-migrate."""
    try:
        # Set up the migration configuration
        MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
        MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
        MONGO_DB = os.getenv("MONGO_DB", "agentops")
        MIGRATIONS_DIR = os.getenv("MIGRATIONS_DIR", str(__import__("pathlib").Path(__file__).resolve().parents[1] / "migrations"))

        # Create the configuration object using SimpleNamespace
        config = SimpleNamespace(
            host=MONGO_HOST,
            port=MONGO_PORT,
            database=MONGO_DB
        )

        # Initialize MigrationManager with config and migrations path
        logger.info("Running database migrations...")
        migration_manager = MigrationManager(config=config, migrations_path=MIGRATIONS_DIR)

        # If any new migration files are added, Below given target_migration has to updated before running the app.
        migration_manager.migrate('upgrade', target_migration='20241103094310')
        logger.info("Migrations applied successfully.")

    except MongoMigrateException as e:
        logger.error(f"Migration failed: {e}")
        raise

async def connect_mongodb():
    global client, database
    host = os.getenv("MONGO_HOST", "127.0.0.1")
    port = os.getenv("MONGO_PORT", "27017")
    url = os.getenv("MONGO_URL") or f"mongodb://{host}:{port}"
    name = os.getenv("MONGO_DB", "agentops")
    client = motor.motor_asyncio.AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
    database = client[name]
    try:
        await database.command("ping")
    except Exception:
        client.close()
        client = None
        database = None
        raise RuntimeError("MongoDB is unavailable. Start MongoDB or configure MONGO_URL.") from None
    logger.info("MongoDB connected successfully")

async def disconnect_mongodb():
    """Disconnect from MongoDB."""
    global client
    if client:
        client.close()
        logger.info("Database disconnected successfully!")
    else:
        logger.info("Database not connected.")
