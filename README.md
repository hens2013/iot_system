
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

### Environment Variables
Create a `.env` file in the root directory with the following content:
```env
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
RABBITMQ_URL=amqp://<username>:<password>@<host>:<port>/
RABBITMQ_QUEUE=<queue-name>
REDIS_URL=redis://<host>:<port>/
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Initialize the Database
```bash
python -c "from services.db import init_db; init_db()"
```

### Run the Application
Start the FastAPI server:
```bash
uvicorn alerting_service.app.alert_service_main:alerting_service_app --host 127.0.0.1 --port 8000 --reload
```

### Start the RabbitMQ Consumer
```bash
python -c "import asyncio; from services.consumer import RabbitMQConsumer; consumer = RabbitMQConsumer(); asyncio.run(consumer.connect())"
```

---

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

---

## Common Issues and Resolutions

### Error: Relation "events" does not exist
If you encounter the following error during execution:
```
2025-01-04 15:50:41,264 - ERROR - Failed to create event: (psycopg2.errors.UndefinedTable) relation "events" does not exist
```
This indicates that the required database tables have not been created. You need to create the tables manually inside the Docker container.

### Steps to Resolve
1. **Access the Dockerized Database**:
   Run the following command to access the database shell inside the Docker container:
   ```bash
   docker exec -it <postgres-container-name> psql -U <username> -d <database-name>
   ```
   Replace `<postgres-container-name>`, `<username>`, and `<database-name>` with the appropriate values for your setup.

2. **Run the Table Creation Queries**:
   Execute the following SQL queries in the database shell to create the required tables:
   ```sql
   -- Table: events
   CREATE TABLE events (
       id SERIAL PRIMARY KEY,
       device_id VARCHAR NOT NULL,
       timestamp TIMESTAMP NOT NULL,
       event_type VARCHAR NOT NULL,
       meta_data JSON
   );

   -- Table: photos
   CREATE TABLE photos (
       id SERIAL PRIMARY KEY,
       uuid VARCHAR NOT NULL,
       photo BYTEA NOT NULL
   );

   -- Table: alerts
   CREATE TABLE alerts (
       id SERIAL PRIMARY KEY,
       event_type VARCHAR NOT NULL,
       description VARCHAR NOT NULL,
       meta_data JSON,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

3. **Verify the Tables**:
   After running the queries, verify that the tables exist using the `\dt` command inside the PostgreSQL shell:
   ```sql
   \dt
   ```

4. **Restart the Application**:
   Once the tables are created, restart the application services to ensure proper operation.

---

## System Components

### FastAPI Application
Provides RESTful APIs for creating and retrieving events and alerts.

### RabbitMQ
Handles asynchronous message queuing for processing events.

### PostgreSQL
Stores events and alerts for persistence and querying.

### Redis
Caches sensor and user data for quick lookups.

---

## Workflow

1. **Event Creation**:
   An event is sent to the `/events/` endpoint.
   The event is validated and published to RabbitMQ.

2. **Event Processing**:
   The RabbitMQ consumer processes the event and evaluates alert criteria.
   Alerts are stored in the database and can be retrieved via `/alerts/get_alerts`.

3. **Caching**:
   Sensor details and authorized user data are cached in Redis to reduce database lookups.

---

