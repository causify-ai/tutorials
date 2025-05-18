FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install tensorflow==2.15.1 \
    && pip install tfx==1.15.1 \
    && pip install pandas matplotlib requests Flask

# Copy all application code (includes realtime_update.py and others)
COPY . .

# Set the working directory to where your pipeline + deploy script is
WORKDIR /app/tutorial_template/tfx_pipeline

# Set the default command to run your deployment script
CMD ["python", "simple_deploy.py"]
