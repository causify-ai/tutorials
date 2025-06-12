# Base Python image
FROM python:3.10-slim

# Set up environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libatlas-base-dev \
    libglib2.0-0 \
    libgomp1 \
    liblapack-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip && pip install \
    jupyter \
    pandas \
    numpy==1.23.5 \
    matplotlib \
    seaborn \
    requests \
    openai \
    griptape \
    scikit-learn \
    statsmodels \
    prophet \
    plotly

# Set working directory
WORKDIR /workspace/griptape

# Copy local code
COPY . /workspace/griptape

# Expose ports (Jupyter + optional API-related ports)
EXPOSE 8888

# Default command
CMD ["./docker_start.sh"]
