FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    vim \
    sudo \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python packages
RUN pip install \
    ipython \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf \
    requests \
    aiohttp \
    pandas \
    statsmodels \
    matplotlib \
    plotly \
    schedule \
    tqdm \
    ipywidgets \
    --no-cache-dir "mcp[cli]" 
    # jupyter-mcp-server 

# Create working directory for installations
RUN mkdir /install

# Copy and run Jupyter extensions install script
ADD install_jupyter_extensions.sh /install
RUN /install/install_jupyter_extensions.sh

# System config and user settings
ADD etc_sudoers /install/
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc

# Version logging (optional)
ADD version.sh /install/
RUN /install/version.sh 2>&1 | tee version.log

# Copy Jupyter startup script
COPY run_jupyter.sh /usr/local/bin/run_jupyter.sh
RUN chmod +x /usr/local/bin/run_jupyter.sh

# Expose Jupyter port
EXPOSE 8888
