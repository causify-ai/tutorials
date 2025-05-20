# Use an official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app:${PATH}"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip cache purge
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Make scripts executable
RUN chmod +x bitcoin_news_sentiment.py

# Expose port for Jupyter
EXPOSE 8888

# Default command: start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--no-browser", "--NotebookApp.token=''"] 