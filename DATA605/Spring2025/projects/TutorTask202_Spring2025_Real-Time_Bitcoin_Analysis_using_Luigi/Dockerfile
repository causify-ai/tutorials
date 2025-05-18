# Dockerfile for Real-Time BTC Analytics Pipeline

FROM python:3.10-slim

WORKDIR /app

COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Optional: display installed packages
RUN pip list

# Default command: load .env and run the pipeline
CMD bash -c "set -a && [ -f .env ] && . .env && set +a && \
    python -m luigi --module coingecko_utils StoreToS3Task --local-scheduler"