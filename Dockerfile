FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the specific project files
COPY TextBlob1.example.ipynb .
COPY TextBlob1.API.ipynb .
COPY TextBlob1_Utils.py .
COPY TextBlob.API.md .
COPY requirements.txt .
COPY main.py .
COPY TextBlob1.example.md .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader stopwords punkt

# Create necessary directories
RUN mkdir -p data figures/html dashboard/assets

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port for Jupyter
EXPOSE 8888

# Command to run when the container starts
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
