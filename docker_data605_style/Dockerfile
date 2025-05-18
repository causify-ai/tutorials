FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo curl systemctl gnupg git vim \
    python3 python3-pip python3-dev python3-venv build-essential

RUN pip3 install --upgrade pip && pip3 install poetry

WORKDIR /app
COPY pyproject.toml /app/
RUN poetry install --no-root
COPY . /app

# ✅ Create Jupyter config and explicitly disable token & password
RUN poetry run python3 -m jupyter_server --generate-config && \
    echo "c.ServerApp.token = ''" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.password = ''" >> /root/.jupyter/jupyter_server_config.py

# Skip extensions
RUN echo "No extensions to install"

COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc
ADD version.sh /install/
RUN /install/version.sh 2>&1 | tee version.log

# ✅ Use Poetry shell to launch without token
EXPOSE 8888
CMD poetry run jupyter lab --config=/root/.jupyter/jupyter_server_config.py --ip=0.0.0.0 --port=8888 --no-browser --allow-root
