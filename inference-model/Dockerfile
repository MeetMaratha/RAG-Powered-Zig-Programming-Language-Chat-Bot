# Chose a Docker image
FROM python:3.12-slim

# Set the working directory
WORKDIR /usr/src/app

# Install dependencies for the application
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential python3-dev curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements
COPY ./requirements.txt .

# Install depedencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the main code
COPY ./main.py .
COPY ./run.sh .

# Expose the port for connection to the application
EXPOSE 8000

# Run the server
CMD ["bash", "./run.sh"]
