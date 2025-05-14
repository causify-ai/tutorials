# Base image with Python
FROM python:3.12-slim

# Arguments from build
ARG AM_CONTAINER_VERSION
ARG INSTALL_DIND
ARG POETRY_MODE
ARG CLEAN_UP_INSTALLATION

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

# Copy project
COPY . /app

# Set up virtual environment & install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

CMD ["bash"]
