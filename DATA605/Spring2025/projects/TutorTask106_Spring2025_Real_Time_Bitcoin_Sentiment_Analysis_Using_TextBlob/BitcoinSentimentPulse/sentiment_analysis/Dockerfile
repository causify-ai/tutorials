FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader punkt averaged_perceptron_tagger

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Create necessary directories
RUN mkdir -p /var/log/sentiment_analysis /data/csv_backups

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    LOG_FILE=/var/log/sentiment_analysis/sentiment_analysis.log

# Run the application
ENTRYPOINT ["/bin/bash", "entrypoint.sh"] 