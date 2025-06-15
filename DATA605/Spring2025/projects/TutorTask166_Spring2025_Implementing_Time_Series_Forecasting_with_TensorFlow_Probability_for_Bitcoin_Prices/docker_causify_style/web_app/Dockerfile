FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create utilities directory
RUN mkdir -p /app/utilities

# Copy the application code
COPY . .

# Copy utilities from parent directory (will be mounted in docker-compose)
# This is a placeholder - the actual utilities will be mounted from the host

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "backend/app.py"] 