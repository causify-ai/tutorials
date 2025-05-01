# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install required Python packages
COPY docker_data605_style/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Download NLTK VADER lexicon
RUN python -m nltk.downloader vader_lexicon

# Expose Prometheus metrics port
EXPOSE 8000

# Default command (no command set because your docker-compose defines it)
CMD ["sleep", "infinity"]
