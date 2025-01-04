from datetime import datetime
import base64
from fastapi import APIRouter, Depends, Query
from ingestion_service.app.models import Photo
from ..models import Alert
from services.db import get_db
from services.cache import RedisCache
from services.consumer import RabbitMQConsumer

alerts_router = APIRouter()
common_fields = {"device_id", "timestamp", "event_type"}

redis_cache = RedisCache()
consumer = RabbitMQConsumer()


# # Define the background RabbitMQ consumer task
async def start_rabbitmq_consumer():
    """
    Starts the RabbitMQ consumer to listen for messages.
    """
    await consumer.connect()  # Establish connection
    await consumer.consume()  # Start consuming messages



@alerts_router.get("/get_alerts")
def get_alerts(
    db=Depends(get_db),
    start_time: datetime = Query(None, description="Start of the time range"),
    end_time: datetime = Query(None, description="End of the time range"),
    event_type: str = Query(None, description="Type of the Alert"),
):
    query = db.query(Alert)

    if start_time:
        query = query.filter(Alert.timestamp >= start_time)
    if end_time:
        query = query.filter(Alert.timestamp <= end_time)
    if event_type:
        query = query.filter(Alert.event_type == event_type)

    alerts = query.all()

    # Collect all UUIDs from meta_data
    uuid_list = [
        alert.meta_data["uuid"]
        for alert in alerts
        if alert.meta_data and "uuid" in alert.meta_data
    ]

    # Bulk query to fetch photos
    photos = (
        db.query(Photo)
            .filter(Photo.uuid.in_(uuid_list))
            .all()
    )

    # Create a mapping of UUID to photo
    uuid_to_photo = {str(photo.uuid): photo.photo for photo in photos}

    # Prepare the result
    result = []
    for alert in alerts:
        photo_base64 = None
        if alert.meta_data and "uuid" in alert.meta_data:
            photo_uuid = alert.meta_data["uuid"]
            if photo_uuid in uuid_to_photo and uuid_to_photo[photo_uuid]:
                photo_base64 = base64.b64encode(uuid_to_photo[photo_uuid]).decode("utf-8")

        result.append(
            {
                "alert_id": alert.id,
                "event_type": alert.event_type,
                "description": alert.description,
                "meta_data": alert.meta_data,
                "created_at": alert.created_at.isoformat(),
                "photo": photo_base64,
            }
        )

    return {"alerts": result}

