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
    pandas \
    matplotlib \
    requests \
    petastorm \
    pyarrow \
    requests \
    torch \
    torchvision \
    torchaudio \


RUN mkdir /install

# Install Jupyter extensions.
# ADD install_jupyter_extensions.sh /install
# RUN /install/install_jupyter_extensions.sh

# Config.
# ADD etc_sudoers /install/
# COPY etc_sudoers /etc/sudoers
# COPY bashrc /root/.bashrc

# Report package versions.
# ADD version.sh /install/
# RUN /install/version.sh 2>&1 | tee version.log

# Jupyter.
# EXPOSE 8888
