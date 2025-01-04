import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from alerting_service.app.api.endpoints import alerts_router
from services.db import get_db
from services.cache import RedisCache
from services.consumer import RabbitMQConsumer
import uvicorn

# Initialize services
redis_cache = RedisCache()
consumer = RabbitMQConsumer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastAPI application

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle the startup and shutdown lifecycle for the application,
    including connecting to RabbitMQ and Redis.
    """
    consumer_task = None
    try:
        logger.info("Starting IoT Alert Service...")

        # Connect to RabbitMQ
        logger.info("Connecting to RabbitMQ...")
        await consumer.connect()
        consumer_task = asyncio.create_task(consumer.consume())
        logger.info("RabbitMQ connected and consumer started.")

        # Connect to Redis
        logger.info("Connecting to Redis...")
        await redis_cache.connect()
        logger.info("Redis connected.")

        # Set up the database connection (if needed)
        get_db()
        logger.info("Database initialized.")

        yield

    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise
    finally:
        # Graceful shutdown
        logger.info("Shutting down IoT Alert Service...")
        if consumer_task:
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                logger.info("RabbitMQ consumer task cancelled.")
        await consumer.close()
        await redis_cache.disconnect()
        logger.info("Resources cleaned up. Shutdown complete.")


# Assign the lifespan context manager to the application
alerting_service_app = FastAPI(
    title="IoT Alert Service",
    lifespan=lifespan,
)

# Include the alerts router
alerting_service_app.include_router(
    alerts_router,
    prefix="/alerts",
    tags=["Alerts"],
)


# Health check endpoint
@alerting_service_app.get("/")
async def health_check():
    """
    Health check endpoint to verify the service status.
    """
    return {"status": "ok", "message": "Alert Service is running"}


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "alerting_service.app.alert_service_main:alerting_service_app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
