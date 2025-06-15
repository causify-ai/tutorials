FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# System update and install core utilities
RUN apt-get update && apt-get -y upgrade && apt-get install -y --no-install-recommends \
    sudo \
    curl \
    gnupg \
    git \
    vim \
    python3 \
    python3-pip \
    python3-dev \
    python3-distutils \
    python3-venv \
    build-essential \
    wget

# Ensure pip is up to date
RUN python3 -m pip install --upgrade pip

# Python version check (optional)
RUN python3 --version && pip3 --version

# Install Python packages
RUN pip3 install \
    ipython \
    tornado==6.1 \
    jupyterlab \
    jupyter-client==7.3.2 \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf

# Create working directory
RUN mkdir /install

# Install Jupyter extensions
COPY install_jupyter_extensions.sh /install/install_jupyter_extensions.sh
RUN sed -i 's/\r$//' /install/install_jupyter_extensions.sh \
 && chmod +x      /install/install_jupyter_extensions.sh \
 && /install/install_jupyter_extensions.sh

# Copy sudoers and bashrc configs
COPY etc_sudoers /install/etc_sudoers
RUN cp /install/etc_sudoers /etc/sudoers

COPY bashrc /install/bashrc
RUN sed -i 's/\r$//' /install/bashrc && cp /install/bashrc /root/.bashrc

# Run version script (optional)
COPY version.sh /install/version.sh
RUN sed -i 's/\r$//' /install/version.sh \
 && chmod +x      /install/version.sh \
 && /install/version.sh 2>&1 | tee version.log

# Install requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Expose Jupyter port
EXPOSE 8888
