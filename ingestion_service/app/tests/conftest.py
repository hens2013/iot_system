import pytest
from unittest.mock import AsyncMock, MagicMock
from services.cache import RedisCache


@pytest.fixture
def client():
    """
    Provides a test client for the FastAPI api.
    """
    from ingestion_service.app.ingestion_service_main import app
    from fastapi.testclient import TestClient

    return TestClient(app)


@pytest.fixture
def mock_redis():
    """
    Mock RedisCache for unit tests.
    """
    redis_cache = MagicMock(spec=RedisCache)
    redis_cache.connect = AsyncMock()
    redis_cache.disconnect = AsyncMock()
    redis_cache.get_sensor = AsyncMock(return_value={"device_type": "access_controller"})
    redis_cache.is_authorized_user = AsyncMock(return_value=True)
    redis_cache.add_sensor = AsyncMock()
    redis_cache.add_authorized_user = AsyncMock()
    return redis_cache
