# Chose Docker image
FROM python:3.12-slim

# Set working directory
WORKDIR /usr/src/app

# Copy requirements file
COPY ./requirements.txt .

# Install dependecies for the application
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential python3-dev gfortran && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the main code
COPY ./chunker_storer.py .

# Expose the port for connection to the application
EXPOSE 8000

# Run the server
CMD ["python", "./chunker_storer.py"]
