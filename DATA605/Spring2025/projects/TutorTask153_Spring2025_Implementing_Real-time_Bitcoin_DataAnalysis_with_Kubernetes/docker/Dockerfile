FROM python:3.12-slim

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

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD ["python", "bitcoin_data_fetcher.py"]