FROM jupyter/scipy-notebook:latest

WORKDIR /home/jovyan/work

COPY . /home/jovyan/work

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

EXPOSE 8888
