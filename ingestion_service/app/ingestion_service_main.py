from fastapi import FastAPI
from ingestion_service.app.api.endpoints import events_router

from services.db import get_db
from services.cache import RedisCache
from contextlib import asynccontextmanager

redis_cache = RedisCache()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    get_db()
    await redis_cache.connect()

    yield

    # Shutdown actions
    await redis_cache.disconnect()


ingestion_service_app = FastAPI(
    title="IoT Ingestion Service"
)

# Pass RedisCache instance to the router
ingestion_service_app.include_router(events_router, prefix="/api/events", tags=["Events"])


@ingestion_service_app.get("/")
async def health_check():
    return {"status": "ok", "message": "Ingestion Service is running"}


def main():
    import uvicorn
    uvicorn.run(
        "ingestion_service_main:ingestion_service_app",
        host="127.0.0.1",
        port=8003,
        reload=True
    )


if __name__ == "__main__":
    main()
