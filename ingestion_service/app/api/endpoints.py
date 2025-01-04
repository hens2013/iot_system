import logging
from datetime import datetime
import uuid
import base64
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Union
from .event_schemas import AccessAttempEvent, SpeedViolationEvent, MotionDetectedEvent
from .validation import validate_mac
from ..models import Event, Photo
from services.db import get_db
from services.cache import RedisCache
from services.publisher import RabbitMQPublisher

# Initialize router, services, and logging
events_router = APIRouter()
redis_cache = RedisCache()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Mapping event types to sensor types
event_to_sensor_type = {
    "access_attempt": "access_controller",
    "motion_detected": "motion_sensor",
    "temperature_reading": "temperature_sensor",
    "humidity_reading": "humidity_sensor",
    "pressure_change": "pressure_sensor",
    "proximity_alert": "proximity_sensor",
    "light_level_change": "light_sensor",
    "gas_leak_detected": "gas_sensor",
    "smoke_detected": "smoke_sensor",
    "water_quality_alert": "water_quality_sensor",
    "chemical_spill_detected": "chemical_sensor",
    "infrared_motion_detected": "infrared_sensor",
    "acceleration_event": "accelerometer",
    "gyroscope_data": "gyroscope",
    "magnetic_field_change": "magnetic_field_sensor",
    "sound_detected": "sound_sensor",
    "liquid_level_change": "level_sensor",
    "radiation_alert": "radiation_sensor",
    "image_captured": "image_sensor",
    "touch_event": "touch_sensor",
    "ultrasonic_distance_measured": "ultrasonic_sensor",
}

@events_router.post("/")
async def create_event(
    event: Union[AccessAttempEvent, SpeedViolationEvent, MotionDetectedEvent],
    db=Depends(get_db),
):
    """
    Create a new event and publish it to RabbitMQ.
    """
    try:
        if not validate_mac(event.device_id):
            raise HTTPException(status_code=400, detail="Invalid MAC address")

        # Check or add sensor details in Redis
        sensor = await redis_cache.get_sensor(event.device_id)
        if not sensor:
            sensor_type = event_to_sensor_type.get(event.event_type, "unknown_sensor")
            sensor_details = {"device_type": sensor_type}
            await redis_cache.add_sensor(event.device_id, sensor_details)
            logger.info(f"Sensor {event.device_id} added to Redis with type {sensor_type}.")

        # Prepare metadata
        meta_data = event.dict(exclude={"device_id", "timestamp", "event_type", "photo_base64"})

        # Handle photo upload for motion detected events
        if isinstance(event, MotionDetectedEvent):
            photo_uuid = str(uuid.uuid4())
            photo_binary = base64.b64decode(event.photo_base64)
            new_photo = Photo(uuid=photo_uuid, photo=photo_binary)
            db.add(new_photo)
            db.commit()
            db.refresh(new_photo)
            meta_data["uuid"] = photo_uuid

        # Store the event in the database
        new_event = Event(
            device_id=event.device_id,
            timestamp=event.timestamp,
            event_type=event.event_type,
            meta_data=meta_data,
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        # Publish the event to RabbitMQ
        process_event = {
            "device_id": event.device_id,
            "event_type": event.event_type,
            "meta_data": meta_data,
        }

        rabbitmq_publisher = RabbitMQPublisher()
        rabbitmq_publisher.connect()
        try:
            rabbitmq_publisher.publish(process_event)
            logger.info(f"Event {new_event.id} published to RabbitMQ.")
        finally:
            rabbitmq_publisher.close()

        return {"message": "Event created successfully", "event_id": new_event.id}

    except Exception as e:
        logger.error(f"Failed to create event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@events_router.get("/get_events")
def get_events(
    db=Depends(get_db),
    start_time: datetime = Query(None, description="Start of the time range"),
    end_time: datetime = Query(None, description="End of the time range"),
    event_type: str = Query(None, description="Type of the event"),
    device_type: str = Query(None, description="Type of the device"),
):
    """
    Retrieve events from the database, filtered by optional parameters.
    """
    try:
        query = db.query(Event)

        if start_time:
            query = query.filter(Event.timestamp >= start_time)
        if end_time:
            query = query.filter(Event.timestamp <= end_time)
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if device_type:
            query = query.filter(Event.meta_data.contains(f'"device_type": "{device_type}"'))

        events = query.all()

        result = [
            {
                "device_id": event.device_id,
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "meta_data": event.meta_data,
            }
            for event in events
        ]

        if not result:
            logger.info("No events found for the given filters.")
        else:
            logger.info(f"Retrieved {len(result)} events.")

        return {"events": result}

    except Exception as e:
        logger.error(f"Failed to retrieve events: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
