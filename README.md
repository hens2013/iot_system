
# IoT Alerting System

## Overview
The IoT Alerting System is designed to process events from IoT devices, trigger alerts based on predefined criteria, and store alerts in a database. It integrates seamlessly with RabbitMQ for message brokering, PostgreSQL for database storage, and Redis for caching.

---

## Features
- **Event Processing**: Handles a variety of IoT events, such as access attempts, speed violations, and motion detection.
- **Alert Triggering**: Generates alerts based on specific criteria for different event types.
- **Scalable Messaging**: Utilizes RabbitMQ for robust message queue management.
- **Efficient Caching**: Uses Redis to cache sensor and authorized user information.
- **Database Integration**: Stores alerts and event metadata in a PostgreSQL database.

---

## Setup Instructions

### Prerequisites
1. **Python**: Ensure Python 3.8+ is installed.
2. **Redis**: Install Redis for caching.
3. **RabbitMQ**: Install RabbitMQ as the message broker.
4. **PostgreSQL**: Set up a PostgreSQL database.
5. **Dependencies**: Install required Python libraries using `pip`.

### Installing RabbitMQ and Redis

#### Install RabbitMQ
1. Update your package index and install RabbitMQ:
   ```bash
   sudo apt update
   sudo apt install rabbitmq-server -y
   ```
2. Enable and start the RabbitMQ service:
   ```bash
   sudo systemctl enable rabbitmq-server
   sudo systemctl start rabbitmq-server
   ```
3. Verify RabbitMQ is running:
   ```bash
   sudo systemctl status rabbitmq-server
   ```

#### Install Redis
1. Update your package index and install Redis:
   ```bash
   sudo apt update
   sudo apt install redis-server -y
   ```
2. Enable and start the Redis service:
   ```bash
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   ```
3. Verify Redis is running:
   ```bash
   redis-cli ping
   ```
   If Redis is running, the response will be `PONG`.

### Installation Steps
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the root directory with the following content:
   ```env
   DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
   RABBITMQ_URL=amqp://<username>:<password>@<host>:<port>/
   RABBITMQ_QUEUE=<queue-name>
   REDIS_URL=redis://<host>:<port>/
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**:
   ```bash
   python -c "from services.db import init_db; init_db()"
   ```

5. **Run the Application**:
   Start the FastAPI server:
   ```bash
   uvicorn alerting_service.app.alert_service_main:alerting_service_app --host 127.0.0.1 --port 8000 --reload
   ```

6. **Start the RabbitMQ Consumer**:
   ```bash
   python -c "import asyncio; from services.consumer import RabbitMQConsumer; consumer = RabbitMQConsumer(); asyncio.run(consumer.connect())"
   ```

### Running with Docker
1. **Install Docker**:
   Ensure Docker and Docker Compose are installed on your system.

2. **Build the Docker Images**:
   ```bash
   docker-compose build
   ```

3. **Run the Services**:
   Start all required services (FastAPI, RabbitMQ, Redis, PostgreSQL):
   ```bash
   docker-compose up
   ```

4. **Access the Application**:
   The application will be available at `http://127.0.0.1:8000`.

5. **Stop the Services**:
   ```bash
   docker-compose down
   ```

---

## API Documentation

### Endpoints

#### 1. **Health Check**
- **Endpoint**: `/`
- **Method**: `GET`
- **Description**: Verifies if the service is running.
- **Response**:
  ```json
  {
    "status": "ok",
    "message": "Alert Service is running"
  }
  ```

#### 2. **Create Event**
- **Endpoint**: `/events/`
- **Method**: `POST`
- **Description**: Creates an event, processes it, and generates alerts if applicable.
- **Request Body**:
  - Example for a motion detected event:
    ```json
    {
      "device_id": "mac-address",
      "timestamp": "2023-01-01T12:00:00",
      "event_type": "motion_detected",
      "meta_data": {
        "confidence": 0.95,
        "photo_base64": "<base64-string>"
      }
    }
    ```
- **Response**:
  ```json
  {
    "message": "Event created successfully",
    "event_id": 1
  }
  ```

#### 3. **Get Events**
- **Endpoint**: `/events/get_events`
- **Method**: `GET`
- **Description**: Retrieves events based on filters.
- **Query Parameters**:
  - `start_time` (optional): Start of the time range.
  - `end_time` (optional): End of the time range.
  - `event_type` (optional): Type of event.
  - `device_type` (optional): Type of device.
- **Response**:
  ```json
  {
    "events": [
      {
        "device_id": "mac-address",
        "timestamp": "2023-01-01T12:00:00",
        "event_type": "motion_detected",
        "meta_data": {
          "confidence": 0.95
        }
      }
    ]
  }
  ```

#### 4. **Get Alerts**
- **Endpoint**: `/alerts/get_alerts`
- **Method**: `GET`
- **Description**: Retrieves alerts based on filters.
- **Query Parameters**:
  - `start_time` (optional): Start of the time range.
  - `end_time` (optional): End of the time range.
  - `event_type` (optional): Type of event.
- **Response**:
  ```json
  {
    "alerts": [
      {
        "alert_id": 1,
        "event_type": "motion_detected",
        "description": "Motion detected with high confidence: 0.95",
        "meta_data": {
          "confidence": 0.95
        },
        "created_at": "2023-01-01T12:00:00",
        "photo": "<base64-encoded-photo>"
      }
    ]
  }
  ```

---

## Alert Criteria

### Criteria for Generating Alerts:
1. **Access Attempt**:
   - Triggered if the user attempting access is not authorized.
   - Example:
     - **Condition**: `user_id` not in authorized users list.
     - **Alert**: Unauthorized access attempt.

2. **Speed Violation**:
   - Triggered if the speed exceeds 100 km/h.
   - Example:
     - **Condition**: `speed_kmh > 100`.
     - **Alert**: Speed violation detected.

3. **Motion Detected**:
   - Triggered if the confidence level of detected motion is greater than 0.9.
   - Example:
     - **Condition**: `confidence > 0.9`.
     - **Alert**: Motion detected with high confidence.

---

## System Explanation

### Components:
1. **FastAPI Application**:
   - Provides RESTful APIs for creating and retrieving events and alerts.
2. **RabbitMQ**:
   - Handles asynchronous message queuing for processing events.
3. **PostgreSQL**:
   - Stores events and alerts for persistence and querying.
4. **Redis**:
   - Caches sensor and user data for quick lookups.

### Workflow:
1. **Event Creation**:
   - An event is sent to the `/events/` endpoint.
   - The event is validated and published to RabbitMQ.
2. **Event Processing**:
   - The RabbitMQ consumer processes the event and evaluates alert criteria.
   - Alerts are stored in the database and can be retrieved via `/alerts/get_alerts`.
3. **Caching**:
   - Sensor details and authorized user data are cached in Redis to reduce database lookups.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.
