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
    vim \
    build-essential \
    libatlas-base-dev \
    libffi-dev \
    libssl-dev \
    libpq-dev

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
RUN mkdir install

RUN pip3 install \
    ipython \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf
 
#RUN pip install --no-cache-dir -r /install/requirements.txt


#RUN mkdir /install

# Install Jupyter extensions.
COPY install_jupyter_extensions.sh /install/
RUN chmod +x/install/install_jupyter_extensions.sh&&/install/install_jupyter_extensions.sh || true

# Config.
ADD etc_sudoers /install/
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc

# Report package versions.
COPY version.sh /install/
RUN chmod +x/install/version.sh 2>&1 | tee version.log
# Set default working directory
WORKDIR /data

# Jupyter.
EXPOSE 8888

# Default command to launch Jupyter
CMD ["jupyter-notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
