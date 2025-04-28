# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir requests apscheduler influxdb-client

# Copy the rest of the application code into the container
COPY . .

# Set the default command to run the script
CMD ["python", "fetch_data.py"]