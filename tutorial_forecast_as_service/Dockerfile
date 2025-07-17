# Use official lightweight Python image.
FROM python:3.12-slim

# Install OS dependencies.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# Set working directory.
WORKDIR /app

# Install Python dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy project files.
COPY . /app/tutorial_forecast_as_service
ENV PYTHONPATH=/app

# Expose port.
EXPOSE 8000

# Start the FastAPI app.
CMD ["uvicorn", "tutorial_forecast_as_service.api.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]
