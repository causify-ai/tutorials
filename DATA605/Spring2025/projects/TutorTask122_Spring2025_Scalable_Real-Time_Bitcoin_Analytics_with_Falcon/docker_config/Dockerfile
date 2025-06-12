FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

# System update and install Redis, utilities, Python, and build tools
RUN apt-get update && apt-get upgrade -y \
 && apt-get install -y --no-install-recommends \
    redis-server \
    sudo \
    curl \
    systemctl \
    gnupg \
    git \
    vim \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libffi-dev \
    pkg-config \
    libhdf5-dev \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --no-cache-dir --upgrade pip

COPY requirements.txt .
# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Jupyter nbextensions
RUN mkdir /install
COPY install_jupyter_extensions.sh /install/
RUN /install/install_jupyter_extensions.sh

# Automatically register the correct kernel inside the container
RUN python3 -m ipykernel install --name falcon_env --display-name "Python (Falcon Container)"
RUN pip3 install --no-cache-dir "uvicorn[standard]"

# Add configuration files
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc

# Report package versions
COPY version.sh /install/
RUN /install/version.sh 2>&1 | tee version.log

# Expose Jupyter port
EXPOSE 8888

# Start Redis, Celery worker, and Uvicorn endpoint
CMD ["bash", "-c", "service redis-server start && celery -A Falcon_Celery_Tasks worker --loglevel=info & uvicorn Falcon_ingest_endpoint:app --host 0.0.0.0 --port 8888 --reload"]