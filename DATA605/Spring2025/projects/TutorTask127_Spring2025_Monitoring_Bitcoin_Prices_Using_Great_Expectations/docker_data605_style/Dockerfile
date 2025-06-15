# FROM ubuntu:20.04
FROM python:3.10-slim
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

# # Install Python.
# RUN apt install -y --no-install-recommends \
#     python3 \
#     python3-pip \
#     python3-dev

# RUN python3 -m pip install --upgrade pip
    
# Install Python packages.
# There is a bug:
#   File "/opt/homebrew/lib/python3.10/site-packages/tornado/iostream.py", line 182, in advance
#   assert 0 < size <= self._size
# for tornado==6.2 and jupyter-client==8.0.2.
# https://discourse.jupyter.org/t/jupyter-notebook-zmq-message-arrived-on-closed-channel-error/17869/10
RUN python3 -m pip install \
    ipython \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf

# Install additional Python packages
RUN python3 -m pip install \
    great_expectations==0.18.13 \
    numpy==1.23.5 \
    pandas==2.1.4 \
    requests==2.31.0 \
    httpx==0.27.0 \
    matplotlib==3.8.4 \
    seaborn==0.13.2 \
    statsmodels==0.14.1 \
    jupyterlab==4.1.6

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

# Jupyter.
EXPOSE 8888

CMD ["jupyter-lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]