FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/raw_data/instant_data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the data collector
CMD ["python", "/app/scripts/get_coingetcko_instant_bitcoin.py"] 