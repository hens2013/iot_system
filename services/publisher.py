import json
import logging
import pika
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class RabbitMQPublisher:
    def __init__(self):
        """
        Initialize RabbitMQPublisher attributes.
        """
        self.connection = None
        self.channel = None

    def connect(self):
        """
        Establish a connection to RabbitMQ and declare the queue.
        """
        try:
            logging.info("Connecting to RabbitMQ...")
            self.connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=config.RABBITMQ_QUEUE, durable=True)
            logging.info("Successfully connected to RabbitMQ.")
        except Exception as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}")
            raise ConnectionError(f"RabbitMQ connection failed: {e}")

    def publish(self, message: dict):
        """
        Publish a message to the RabbitMQ queue.

        :param message: The message to be published, as a dictionary.
        """
        if not self.channel:
            logging.error("RabbitMQ connection not initialized. Call 'connect()' first.")
            raise ConnectionError("RabbitMQ connection not initialized.")

        try:
            logging.info(f"Publishing message to queue {config.RABBITMQ_QUEUE}: {message}")
            self.channel.basic_publish(
                exchange='',
                routing_key=config.RABBITMQ_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)  # Persistent messages
            )
            logging.info("Message published successfully.")
        except Exception as e:
            logging.error(f"Failed to publish message: {e}")
            raise RuntimeError(f"Publishing message failed: {e}")

    def close(self):
        """
        Close the RabbitMQ connection.
        """
        if self.connection:
            try:
                logging.info("Closing RabbitMQ connection...")
                self.connection.close()
                logging.info("RabbitMQ connection closed.")
            except Exception as e:
                logging.error(f"Error while closing RabbitMQ connection: {e}")
