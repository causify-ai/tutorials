# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('punkt', quiet=True)"

# Download TextBlob corpora
RUN python -m textblob.download_corpora

# Create directories for data and figures
RUN mkdir -p data figures

# Copy the rest of your code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the main script by default
CMD ["python", "main.py"]
