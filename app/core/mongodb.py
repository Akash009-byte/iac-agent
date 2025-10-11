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
    return database

async def run_migrations():
    """Run database migrations using mongo-migrate."""
    try:
        # Set up the migration configuration
        MONGO_HOST = os.getenv("MONGO_HOST")
        MONGO_PORT = int(os.getenv("MONGO_PORT"))
        MONGO_DB = os.getenv("MONGO_DB")
        MIGRATIONS_DIR = os.getenv("MIGRATIONS_DIR")

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
    """Attempt to connect to MongoDB and set the global client and database."""
    global client, database
    try:
        mongo_db_host = os.getenv('MONGO_HOST')
        mongo_db_port = os.getenv('MONGO_PORT')
        mongo_db_name = os.getenv('MONGO_DB')
        mongo_db_url = f"mongodb://{mongo_db_host}:{mongo_db_port}"

        if not mongo_db_url:
            raise ValueError("MONGO_DB_URL is not set")

        # Initialize the MongoDB client
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_db_url)
        database = client[mongo_db_name]

        # Verify the connection by listing collections or similar operation
        await client.server_info()
        logger.info("Database connected successfully!")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise

async def disconnect_mongodb():
    """Disconnect from MongoDB."""
    global client
    if client:
        client.close()
        logger.info("Database disconnected successfully!")
    else:
        logger.info("Database not connected.")
        