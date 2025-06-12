# Use a slim Python base image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

FROM python:3.10-slim

WORKDIR /workspace

# Copy all project files
COPY . /workspace

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose Jupyter port
EXPOSE 8888

# Run Jupyter when container starts
CMD ["bash", "./run_jupyter.sh"]
