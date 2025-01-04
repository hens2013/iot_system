import aioredis
import json
import logging
from typing import Optional
from config import config

# Redis keys for storing data
REDIS_SENSOR_KEY = "registered_sensors"
REDIS_AUTHORIZED_USERS_KEY = "authorized_users"


class RedisCache:
    def __init__(self):
        """
        Initialize RedisCache with the Redis URL from the configuration.
        """
        self.redis_url = config.REDIS_URL
        self.redis = None

    async def connect(self):
        """
        Initialize the Redis connection.
        """
        try:
            logging.info(f"Connecting to Redis at {self.redis_url}")
            self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)

            # Check the connection
            if not await self.redis.ping():
                raise ConnectionError("Ping to Redis failed.")

            logging.info("Successfully connected to Redis.")
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Redis connection failed: {e}")

    async def disconnect(self):
        """
        Close the Redis connection.
        """
        if self.redis:
            try:
                logging.info("Disconnecting from Redis.")
                await self.redis.close()
                self.redis = None
                logging.info("Redis disconnected successfully.")
            except Exception as e:
                logging.error(f"Error while disconnecting from Redis: {e}")

    async def ensure_connection(self):
        """
        Ensure the Redis connection is active and reconnect if necessary.
        """
        if not self.redis:
            logging.warning("Redis connection is not active. Reconnecting...")
            await self.connect()

    async def get_sensor(self, device_id: str) -> Optional[dict]:
        """
        Fetch sensor details from Redis.

        :param device_id: The unique ID of the sensor.
        :return: Sensor details as a dictionary or None if not found.
        """
        await self.ensure_connection()
        try:
            logging.info(f"Fetching sensor details for device_id: {device_id}")
            data = await self.redis.hget(REDIS_SENSOR_KEY, device_id)
            if data:
                logging.info(f"Sensor details found for device_id: {device_id}")
                return json.loads(data)
            logging.info(f"No sensor details found for device_id: {device_id}")
            return None
        except Exception as e:
            logging.error(f"Error fetching sensor for device_id {device_id}: {e}")
            return None

    async def add_sensor(self, device_id: str, details: dict):
        """
        Add a sensor to the Redis cache.

        :param device_id: The unique ID of the sensor.
        :param details: A dictionary of sensor details to store.
        """
        await self.ensure_connection()
        try:
            logging.info(f"Adding sensor {device_id} to Redis.")
            await self.redis.hset(REDIS_SENSOR_KEY, device_id, json.dumps(details))
            logging.info(f"Sensor {device_id} added successfully.")
        except Exception as e:
            logging.error(f"Error adding sensor {device_id}: {e}")

    async def is_authorized_user(self, user_id: str) -> bool:
        """
        Check if a user is authorized.

        :param user_id: The unique ID of the user.
        :return: True if the user is authorized, False otherwise.
        """
        await self.ensure_connection()
        try:
            authorized = await self.redis.sismember(REDIS_AUTHORIZED_USERS_KEY, user_id)
            logging.info(f"User {user_id} authorization status: {authorized}")
            return authorized
        except Exception as e:
            logging.error(f"Error checking authorization for user_id {user_id}: {e}")
            return False

    async def add_authorized_user(self, user_id: str):
        """
        Add a user to the authorized users list.

        :param user_id: The unique ID of the user.
        """
        await self.ensure_connection()
        try:
            logging.info(f"Adding user {user_id} to authorized users list.")
            await self.redis.sadd(REDIS_AUTHORIZED_USERS_KEY, user_id)
            logging.info(f"User {user_id} added to authorized users successfully.")
        except Exception as e:
            logging.error(f"Error adding authorized user {user_id}: {e}")
