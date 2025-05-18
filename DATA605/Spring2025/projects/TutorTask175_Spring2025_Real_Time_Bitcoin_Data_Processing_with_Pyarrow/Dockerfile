# Base Python image
FROM python:3.10-slim

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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
    libffi-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
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
    pyarrow \
    scikit-learn \
    statsmodels \
    prophet \
    plotly \
    pmdarima \
    weasyprint \
    ipython \
    notebook \
    openpyxl \
    tzdata

# Set working directory
WORKDIR /workspace/bitcoin-pyarrow

# Copy project files into container
COPY . /workspace/bitcoin-pyarrow

# Expose ports
EXPOSE 8888

# Default command to start Jupyter Notebook (if applicable)
CMD ["bash", "entrypoint.sh"]
