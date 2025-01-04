

FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files to the container
COPY . /app

# Copy the requirements file and install dependencies
COPY ingestion_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install testing dependencies
#COPY ingestion_service/test_requirements.txt ./ingestion_requirements.txt
#RUN pip install --no-cache-dir -r test_requirements.txt


RUN pytest ingestion_service/app/tests
# Copy the entire project into the container
COPY . /app

# Expose application port
EXPOSE 5000

# Run the application
CMD ["uvicorn", "ingestion_service.app.ingestion_service_main:ingestion_service_app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
