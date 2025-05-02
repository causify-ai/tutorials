FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

# 1. Fix base system and repositories
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        software-properties-common \
        apt-utils \
        libsoup2.4-1 && \
    add-apt-repository universe && \
    apt-get update && \
    apt-get -y upgrade

# 2. Install system utilities (FIXED formatting)
RUN apt-get install -y --no-install-recommends \
        sudo \
        curl \
        systemd \
        gnupg \
        git \
        vim && \
    rm -rf /var/lib/apt/lists/*

# 3. Install Python stack
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
        libgomp1 \
        libgl1 \
        libsm6 \
        libxext6 \
        libxrender1 && \
    rm -rf /var/lib/apt/lists/*

# 4. Core Python packages
RUN python3 -m pip install --upgrade pip && \
    pip3 install \
        joblib==1.2.0 \
        pycaret==3.0.0 \
        pandas \
        requests \
        plotly \
        jupyterlab

# 5. ZMQ/tornado fix
RUN pip3 install \
        ipython \
        jupyterlab==3.6.3 \
        notebook==6.5.4 \
        jupyter-client==7.4.9 \
        jupyter-server==2.7.0 \
        traitlets==5.9.0 \
        jupyter-contrib-core \
        jupyter-contrib-nbextensions \
        psycopg2-binary \
        yapf

# 6. Configuration files
RUN mkdir -p /install
COPY install_jupyter_extensions.sh /install/
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc

# 7. Install extensions
RUN chmod +x /install/install_jupyter_extensions.sh && \
    /install/install_jupyter_extensions.sh && \
    chmod 440 /etc/sudoers

EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]

