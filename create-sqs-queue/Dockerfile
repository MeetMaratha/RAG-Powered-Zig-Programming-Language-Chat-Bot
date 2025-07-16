# Chose a Docker image
FROM python:3.12-slim

# Set the working directory
WORKDIR /usr/src/app

# Install dependencies for the application
RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ./requirements.txt .

# Install depedencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the main code
COPY ./main.py .

# Run the server
CMD ["python", "./main.py"]
