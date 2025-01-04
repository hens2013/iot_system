import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from alerting_service.app.models import Alert
from services.consumer import RabbitMQConsumer  # Update to the correct import path
from datetime import datetime


@pytest.fixture
def mock_config():
    with patch("services.consumer.config") as mock_config:
        mock_config.RABBITMQ_URL = "mock_url"
        mock_config.RABBITMQ_QUEUE = "mock_queue"
        yield mock_config


@pytest.fixture
def mock_db_session():
    with patch("services.consumer.SessionLocal") as mock_session_local:
        session_mock = MagicMock()
        mock_session_local.return_value = session_mock
        yield session_mock


@pytest.mark.asyncio
async def test_consumer_connect(mock_config):
    consumer = RabbitMQConsumer()

    with patch("services.consumer.aio_pika.connect_robust", new_callable=AsyncMock) as mock_connect:
        mock_channel = AsyncMock()
        mock_connect.return_value.channel.return_value = mock_channel
        mock_queue = AsyncMock()
        mock_channel.declare_queue.return_value = mock_queue

        await consumer.connect()

        assert consumer.connection is not None
        assert consumer.channel is not None
        assert consumer.queue is not None
        mock_channel.declare_queue.assert_called_with("mock_queue", durable=True)


@pytest.mark.asyncio
async def test_consumer_process_event(mock_config, mock_db_session):
    consumer = RabbitMQConsumer()
    event = {
        "event_type": "speed_violation",
        "meta_data": {"speed_kmh": 120}
    }

    await consumer.process_event(event)

    alert = mock_db_session.add.call_args[0][0]
    assert isinstance(alert, Alert)
    assert alert.event_type == "speed_violation"
    assert "Speed violation detected" in alert.description
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_consumer_close(mock_config):
    consumer = RabbitMQConsumer()
    consumer.connection = AsyncMock()

    await consumer.close()

    consumer.connection.close.assert_called_once()
