import pytest
from unittest.mock import MagicMock, patch
from services.publisher import RabbitMQPublisher
import json
import pika


@pytest.fixture
def mock_config():
    # Mock the configuration
    with patch("services.publisher.config") as mock_config:
        mock_config.RABBITMQ_URL = "mock_url"
        mock_config.RABBITMQ_QUEUE = "mock_queue"
        yield mock_config


@pytest.fixture
def mock_pika():
    # Mock pika.BlockingConnection and its behavior
    with patch("services.publisher.pika.BlockingConnection") as mock_connection:
        # Mock connection and channel
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel

        # Mock queue_declare
        mock_channel.queue_declare.return_value = None

        yield mock_connection, mock_channel


def test_publisher_publish(mock_config, mock_pika):
    mock_connection, mock_channel = mock_pika
    publisher = RabbitMQPublisher()

    # Set the mock channel in the publisher
    publisher.channel = mock_channel

    message = {"event_type": "test_event", "meta_data": {"key": "value"}}

    # Call the publish method
    publisher.publish(message)

    # Verify that basic_publish was called with the correct arguments
    mock_channel.basic_publish.assert_called_once_with(
        exchange="",
        routing_key="mock_queue",
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2),
    )


def test_publisher_close(mock_config, mock_pika):
    mock_connection, _ = mock_pika
    publisher = RabbitMQPublisher()

    # Set the mock connection in the publisher
    publisher.connection = mock_connection.return_value

    # Call the close method
    publisher.close()

    # Verify that close was called on the connection
    publisher.connection.close.assert_called_once()
