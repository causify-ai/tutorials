# Base image
FROM python:3.10-slim

# Set environment variables
ENV DAGSTER_HOME=/dagster_home
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create Dagster home directory
RUN mkdir -p /dagster_home

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -e ".[dev]"
RUN pip install pandas matplotlib numpy seaborn statsmodels dagster dagster-cloud

# Expose Dagster web server port
EXPOSE 3000

# Run Dagster dev server
CMD ["dagster", "dev", "--host", "0.0.0.0", "--port", "3000"]
