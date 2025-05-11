FROM apache/airflow:2.7.3

USER root
RUN apt-get update && apt-get install -y git curl vim gcc g++ build-essential

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
