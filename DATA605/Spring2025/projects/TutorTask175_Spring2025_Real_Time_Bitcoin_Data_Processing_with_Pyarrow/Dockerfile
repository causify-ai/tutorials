FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Update and upgrade base packages
RUN apt-get -y update && apt-get -y upgrade

# Install system utilities and Python
RUN apt-get install -y --no-install-recommends \
    sudo \
    curl \
    gnupg \
    git \
    vim \
    python3 \
    python3-pip \
    python3-dev

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install Python packages including Jupyter and PyArrow
RUN pip3 install \
    ipython \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    jupyter \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    pyarrow \
    pandas \
    requests \
    matplotlib \
    numpy \
    psycopg2-binary \
    yapf

# Create working directory
RUN mkdir /install

# # Install Jupyter extensions
# COPY install_jupyter_extensions.sh /install/
# RUN chmod +x /install/install_jupyter_extensions.sh && /install/install_jupyter_extensions.sh

# Set up sudoers and bashrc
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc

# Report version info
COPY version.sh /install/
RUN chmod +x /install/version.sh && /install/version.sh 2>&1 | tee /install/version.log

# Copy all project files (if needed)
COPY . /app
WORKDIR /app

# # Expose Jupyter port
# EXPOSE 8888

# # Run Jupyter Notebook
# CMD ["bash", "run_jupyter.sh"]
