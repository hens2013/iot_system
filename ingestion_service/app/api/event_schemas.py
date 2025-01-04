from pydantic import BaseModel, Field
from datetime import datetime


class BaseEvent(BaseModel):
    device_id: str = Field(..., description="MAC Address of the device")
    timestamp: datetime
    event_type: str


class AccessAttempEvent(BaseEvent):
    user_id: str


class SpeedViolationEvent(BaseEvent):
    speed_kmh: int
    location: str



class MotionDetectedEvent(BaseEvent):
    zone: str
    confidence: float
    photo_base64: str
