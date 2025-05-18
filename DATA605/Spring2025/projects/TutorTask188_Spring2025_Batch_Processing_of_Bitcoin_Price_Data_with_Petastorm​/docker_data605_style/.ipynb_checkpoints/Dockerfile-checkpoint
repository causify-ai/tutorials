FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Update and upgrade
RUN apt-get -y update && apt-get -y upgrade

RUN apt-get install -y --no-install-recommends \
    sudo \
    curl \
    git \
    vim \
    python3 \
    python3-pip \
    python3-dev \
    build-essential

# Upgrade pip
RUN python3 -m pip install --upgrade pip

RUN mkdir /install

# Copy and install Python packages from requirements.txt
RUN pip3 install notebook \
    pandas \
    matplotlib \
    requests \
    petastorm \
    pyarrow==0.17.1 \
    requests \
    torch \
    torchvision \
    tensorflow-cpu \
    scikit-learn \
    fastparquet

# Create install directory (for optional files/scripts)
#RUN mkdir install

# Install Jupyter extensions if script is present
COPY install_jupyter_extensions.sh /install/
RUN chmod +x /install/install_jupyter_extensions.sh && /install/install_jupyter_extensions.sh || true

# Optional config files
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc

# Track versions
COPY version.sh /install/
RUN chmod +x /install/version.sh && /install/version.sh 2>&1 | tee /install/version.log

# Set default working directory
WORKDIR /data

# Expose Jupyter port
EXPOSE 8888

# Default command to launch Jupyter
CMD ["jupyter-notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
