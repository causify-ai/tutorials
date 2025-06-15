# Use an official Python 3.10 image
FROM python:3.10-slim

# Install any system deps you need
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      git \
      curl \
      bash \
      yq \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only requirements first (for better caching)
COPY requirements.txt ./

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Make sure our scripts are executable
RUN chmod +x scripts/*.sh scripts/*.py mains/*.py

RUN pip install -e .

# No default entrypoint - let docker-compose.yml specify the command
