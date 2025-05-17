FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get -y upgrade

# System utilities
RUN apt install -y --no-install-recommends \
    sudo curl systemctl gnupg git vim

# Python 3 & pip
RUN apt install -y --no-install-recommends python3 python3-pip python3-dev
RUN python3 -m pip install --upgrade pip

# Jupyter & extensions (pin tornado/jupyter-client versions)
RUN pip3 install \
    ipython \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf

RUN mkdir /install
ADD install_jupyter_extensions.sh /install/
RUN /install/install_jupyter_extensions.sh

# Sudoers & bashrc
ADD etc_sudoers /install/
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc

# Report versions
ADD version.sh /install/
RUN /install/version.sh 2>&1 | tee version.log

EXPOSE 8888

# Core Python data libs + Ollama client + Dash/Plotly
RUN pip3 install pandas numpy requests ollama plotly dash
