# Use Python base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files to the container
COPY . /app

# Copy the requirements file and install dependencies
COPY alerting_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

## Install testing dependencies
#COPY alert_service/test_requirements.txt ./alert_requirements.txt
#RUN pip install --no-cache-dir -r test_requirements.txt

# Run the tests during the build process (optional)
RUN pytest alerting_service/app/tests

# Expose the FastAPI port
EXPOSE 8000

# Set the environment variable for FastAPI
ENV PYTHONUNBUFFERED=1

# Default command to run the application
CMD ["uvicorn", "alerting_service.app.alert_service_main:alerting_service_app", "--host", "0.0.0.0", "--port", "8000"]
