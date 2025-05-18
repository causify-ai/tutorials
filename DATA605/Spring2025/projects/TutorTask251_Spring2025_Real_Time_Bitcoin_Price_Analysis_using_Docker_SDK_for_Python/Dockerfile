# --- BTC Fetcher Job Image ---
FROM python:3.10-slim AS btc-fetcher
WORKDIR /app
COPY fetch_btc_data.py .
COPY docker_sdk_utils.py .
RUN pip install requests influxdb-client

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

RUN ln -s /usr/bin/python3 /usr/bin/python

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
    apscheduler\
    influxdb-client\
    docker\
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf\
    pandas\
    matplotlib\
    requests\
    numpy\
    statsmodels

RUN mkdir /install

# Install Jupyter extensions.
ADD docker_data605_style/install_jupyter_extensions.sh /install/
RUN /install/install_jupyter_extensions.sh

# Config.
#ADD etc_sudoers /install/
COPY docker_data605_style/etc_sudoers /etc/sudoers
COPY docker_data605_style/bashrc /root/.bashrc

# Report package versions.
ADD docker_data605_style/version.sh /install/
RUN /install/version.sh 2>&1 | tee version.log

# Copy main project files from the parent directory (project root)
COPY ../main.py /app/
COPY ../docker_sdk_utils.py /app/
COPY ../docker_sdk.example.ipynb /app/
COPY fetch_btc_data.py /app/
COPY logger_config.py /app/
COPY ../docker_sdk.API.ipynb /app/
COPY ../docker_sdk.example.py /app/
COPY ../analysis/analyze.py /app/
# COPY ../requirements.txt /app/

# Jupyter.
EXPOSE 8888

# Set default command to start Jupyter Notebook
# To run a demonstration script instead of Jupyter, change CMD to:
# CMD ["python", "docker_sdk.example.py"]
CMD ["jupyter-notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token=", "--NotebookApp.password="]


