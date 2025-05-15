FROM python:3.9-slim

# Install build tools and libraries for pandas + psycopg2-binary
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    libffi-dev \
    libbz2-dev \
    liblzma-dev \
    libssl-dev \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir setuptools wheel

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

# Expose port for Prometheus metrics
EXPOSE 8000

CMD ["python", "bitcoin_data_fetcher.py"]