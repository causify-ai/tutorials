FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python packages with specific versions
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    keras>=2.14.0 \
    newsapi>=0.1.1 \
    newsapi-python>=0.2.7 \
    numpy>=2.2.5 \
    pandas>=2.2.3 \
    plotly>=6.1.0 \
    psycopg2-binary>=2.9.10 \
    pytz>=2025.2 \
    scikit-learn>=1.6.1 \
    statsmodels>=0.14.4 \
    streamlit>=1.45.1 \
    tensorflow>=2.14.0 \
    tensorflow-probability>=0.25.0 \
    textblob>=0.19.0 \
    trafilatura>=2.0.0 \
    yfinance>=0.2.61

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs && \
    mkdir -p /app/data/sentiment

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=5001", "--server.address=0.0.0.0"]