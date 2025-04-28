FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

# Update and upgrade
RUN apt-get -y update
RUN apt-get -y upgrade

# Install system utilities
RUN apt install -y --no-install-recommends \
    sudo \
    curl \
    systemctl \
    gnupg \
    git \
    vim

# Install Python
RUN apt install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install Python packages
RUN pip3 install \
    ipython \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf

# Create install directory
RUN mkdir /install

# Install Jupyter extensions
ADD install_jupyter_extensions.sh /install
RUN chmod +x /install/install_jupyter_extensions.sh
RUN /install/install_jupyter_extensions.sh

# Configurations
ADD etc_sudoers /install/
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc

# Report package versions
ADD version.sh /install/
RUN /install/version.sh 2>&1 | tee version.log

# Copy startup scripts inside container
COPY run_jupyter.sh /run_jupyter.sh
COPY docker_jupyter.sh /docker_jupyter.sh

# Make startup scripts executable
RUN chmod +x /run_jupyter.sh
RUN chmod +x /docker_jupyter.sh

# Expose Jupyter port
EXPOSE 8888

