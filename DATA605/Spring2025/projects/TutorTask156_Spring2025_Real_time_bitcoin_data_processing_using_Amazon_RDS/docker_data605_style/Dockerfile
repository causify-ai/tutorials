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
    
# Install all Python packages for Bitcoin RDS project
RUN pip install \
    ipython \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    requests \
    scikit-learn \
    python-dotenv \
    notebook \
    jupyterlab \
    plotly \
    streamlit

RUN mkdir /install

# Install Jupyter extensions.
ADD install_jupyter_extensions_copy.sh /install/install_jupyter_extensions.sh
RUN /install/install_jupyter_extensions.sh

# Config.
ADD etc_sudoers_copy /install/etc_sudoers
COPY etc_sudoers_copy /etc/sudoers
COPY bashrc_copy /root/.bashrc


# Report package versions.
ADD version.sh /install/
RUN /install/version.sh 2>&1 | tee version.log

# Jupyter.
EXPOSE 8888

# Set up working directory for project
WORKDIR /project

# Add a command to start Jupyter when container runs
COPY run_jupyter.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/run_jupyter.sh
CMD ["/usr/local/bin/run_jupyter.sh"]
