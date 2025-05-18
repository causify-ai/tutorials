# FROM python:3.10-slim

# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements first to leverage Docker cache
# COPY requirements.txt .

# # Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Download NLTK data (required by sentiment_analyzer.py)
# RUN python -c "import nltk; nltk.download('vader_lexicon')"

# # Copy the application files
# COPY . .

# # Create necessary directories
# RUN mkdir -p templates cache

# # Expose the Flask port
# EXPOSE 5000

# # Set the default command
# CMD ["python", "bitcoinchatbot.py", "--web"]


FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NLTK data download
RUN python -c "import nltk; nltk.download('vader_lexicon')"

# Copy application code
COPY . .

EXPOSE 8501

# Command to run when container starts
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
