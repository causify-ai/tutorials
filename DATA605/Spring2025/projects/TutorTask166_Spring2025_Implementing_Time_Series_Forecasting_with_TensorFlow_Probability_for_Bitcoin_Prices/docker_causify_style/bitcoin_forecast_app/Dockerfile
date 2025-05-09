FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src and utilities directories
COPY src src
COPY utilities utilities

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Make entrypoint script executable (use the correct path)
RUN chmod +x bitcoin_forecast_app/entrypoint.sh

# Set entrypoint (use the correct path)
ENTRYPOINT ["bash", "bitcoin_forecast_app/entrypoint.sh"] 