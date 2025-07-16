# Chose a Docker image
FROM python:3.12-slim

# Set the working directory
WORKDIR /usr/src/app

# Install dependencies for the application
RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Install depedencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests

# Copy the main code
COPY ./make_this_event_driven.py .

# Run the server
CMD ["python", "./make_this_event_driven.py"]
