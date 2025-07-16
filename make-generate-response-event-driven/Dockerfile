# Chose Docker image
FROM python:3.12-slim

# Set working directory
WORKDIR /usr/src/app

# Copy requirements file
COPY ./requirements.txt .

# Install dependecies for the application
RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the main code
COPY ./make_this_event_driven.py .

# Run the server
CMD ["python", "./make_this_event_driven.py"]
