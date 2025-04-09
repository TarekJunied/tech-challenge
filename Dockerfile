FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the script into the container
COPY log_watchdog.py .

# Install only what we need
RUN apt-get update && apt-get install -y \
    libffi-dev \
    libssl-dev \
    --fix-missing && \
    rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip install --no-cache-dir opcua paho-mqtt influxdb-client

# Run the logging script
CMD ["python", "log_watchdog.py"]

