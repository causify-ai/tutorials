FROM python:3.9-slim

# Install system dependencies (for psycopg2 etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy script(s)
COPY fetch_bitcoin_price.py .
COPY bitcoin_utils.py .
COPY bitcoin_pipeline.py .
COPY compile_pipeline.py .

# Install Python dependencies
RUN pip install --no-cache-dir \
    requests \
    pandas \
    sqlalchemy \
    psycopg2-binary \
    kfp==1.8.22

# Set default command (used by Kubeflow)
CMD ["python", "fetch_bitcoin_price.py"]
