FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

# Update and upgrade system
RUN apt-get -y update && apt-get -y upgrade

# Install system utilities
RUN apt-get install -y --no-install-recommends \
    sudo curl systemctl gnupg git vim

# Install Python and dependencies
RUN apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install system-level build dependencies (for econml, numpy, etc.)
RUN apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    gcc \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    libffi-dev \
    libssl-dev

# Install base Python packages
RUN pip3 install \
    ipython tornado==6.1 \
    jupyter-client==7.3.2 \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary yapf

# Copy install scripts and config
RUN mkdir /install
ADD install_jupyter_extensions.sh /install
RUN chmod +x /install/install_jupyter_extensions.sh && /install/install_jupyter_extensions.sh

ADD version.sh /install/
RUN /install/version.sh 2>&1 | tee version.log

COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc
COPY run_jupyter.sh /run_jupyter.sh
COPY docker_jupyter.sh /docker_jupyter.sh
RUN chmod +x /run_jupyter.sh /docker_jupyter.sh

# Copy and install Python requirements
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Expose Jupyter
EXPOSE 8888
