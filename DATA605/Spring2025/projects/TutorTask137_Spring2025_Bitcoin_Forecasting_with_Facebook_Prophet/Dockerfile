FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

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

# Install Python packages (with pinned versions)
RUN pip3 install --no-cache-dir \
    jupyter==1.0.0 \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    requests \
    beautifulsoup4 \
    matplotlib \
    plotly \
    prophet \
    scikit-learn \
    numpy \
    seaborn \
    pandas \
    streamlit \
    tensorflow \
    ipython \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf

# Create install directory
RUN mkdir /install

# Install Jupyter extensions
ADD install_jupyter_extensions.sh /install/
RUN chmod +x /install/install_jupyter_extensions.sh && /install/install_jupyter_extensions.sh

# Config files
ADD etc_sudoers /install/
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc

# Version report
ADD version.sh /install/
RUN /install/version.sh 2>&1 | tee version.log

# Jupyter port
EXPOSE 8888

