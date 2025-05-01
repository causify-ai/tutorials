FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update
RUN apt-get -y upgrade

# Install system utilities.
RUN apt install -y --no-install-recommends \
    sudo \
    curl \
    systemctl \
    gnupg \
    git \
    vim

# Install Python.
RUN apt install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev

RUN python3 -m pip install --upgrade pip
    
# Install Python packages.
# There is a bug:
#   File "/opt/homebrew/lib/python3.10/site-packages/tornado/iostream.py", line 182, in advance
#   assert 0 < size <= self._size
# for tornado==6.2 and jupyter-client==8.0.2.
# https://discourse.jupyter.org/t/jupyter-notebook-zmq-message-arrived-on-closed-channel-error/17869/10
RUN pip3 install \
    ipython \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf

RUN mkdir /install

# Install Jupyter extensions.
ADD install_jupyter_extensions.sh /install
RUN /install/install_jupyter_extensions.sh

# Config.
ADD etc_sudoers /install/
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc

# Report package versions.
ADD version.sh /install/
RUN /install/version.sh 2>&1 | tee version.log

FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your application files into the container
COPY . /app

# Install system dependencies for numpy/scikit-learn
RUN apt-get update && apt-get install -y \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies using pip
RUN pip install --upgrade pip
RUN pip install \
    requests \
    pandas \
    matplotlib \
    cloudpickle \
    ipywidgets \
    scikit-learn \
    pycaret

# Optional: Install Jupyter if you plan to run notebooks inside Docker
RUN pip install notebook

# Expose port 8888 for Jupyter notebook (if using)
EXPOSE 8888
