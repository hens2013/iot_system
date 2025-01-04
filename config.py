import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")
    DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "yes"]
    ALERT_LOG_FILE = os.getenv("ALERT_LOG_FILE")


config = Config()
