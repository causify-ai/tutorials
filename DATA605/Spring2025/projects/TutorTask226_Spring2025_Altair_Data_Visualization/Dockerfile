# Use lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install required Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8080

# Start the FastAPI app
CMD ["uvicorn", "Altair_API:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
