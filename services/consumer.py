import json
import logging
import aio_pika
from sqlalchemy.orm import Session
from alerting_service.app.models import Alert
from services.cache import RedisCache
from services.db import SessionLocal
from config import config
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
redis_cache = RedisCache()


class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self):
        """
        Establish an asynchronous connection to RabbitMQ and declare the queue.
        """
        logging.info("Connecting to RabbitMQ...")
        self.connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        # await self.channel.set_qos(prefetch_count=1)
        self.queue = await self.channel.declare_queue(config.RABBITMQ_QUEUE, durable=True)
        logging.info("Connected to RabbitMQ and queue declared.")

    async def consume(self):
        """
        Start consuming messages from RabbitMQ asynchronously.
        """
        logging.info("Starting RabbitMQ consumer...")
        await self.queue.consume(self.callback, no_ack=False)

    async def callback(self, message: aio_pika.IncomingMessage):
        """
        Callback function to process each message.
        """
        async with message.process():
            try:
                event = json.loads(message.body)
                logging.info(f"Received event: {event}")
                await self.process_event(event)
            except Exception as e:
                logging.error(f"Failed to process message: {e}")

    async def process_event(self, event):
        """
        Process the event and decide whether to trigger an alert. Store alerts in PostgreSQL.
        """
        session: Session = SessionLocal()

        try:
            alert_description = None
            event_type = event.get("event_type")

            if event_type == "access_attempt":
                user_id = event.get("meta_data", {}).get("user_id")

                authorized = await redis_cache.is_authorized_user(user_id)
                if not authorized:
                    alert_description = f"user is not authorized to access"

            elif event_type == "speed_violation":
                speed = event.get("meta_data", {}).get("speed_kmh", 0)
                if speed > 100:
                    alert_description = f"Speed violation detected: {speed} km/h"

            elif event_type == "motion_detected":
                confidence = event.get("meta_data", {}).get("confidence", 0)
                if confidence > 0.9:
                    alert_description = f"Motion detected with high confidence: {confidence}"

            else:
                logging.info(f"No alert generated for event type: {event_type}")

            if alert_description:
                logging.warning(alert_description)

                new_alert = Alert(
                    event_type=event_type,
                    description=alert_description,
                    meta_data=event.get("meta_data"),
                    created_at=datetime.now()
                )

                session.add(new_alert)
                session.commit()
                logging.info(f"Alert stored in database: {alert_description}")

        except Exception as e:
            logging.error(f"Error processing event: {e}")
            session.rollback()

        finally:
            session.close()

    async def close(self):
        """
        Close RabbitMQ connection.
        """
        if self.connection:
            await self.connection.close()
            logging.info("RabbitMQ connection closed.")
