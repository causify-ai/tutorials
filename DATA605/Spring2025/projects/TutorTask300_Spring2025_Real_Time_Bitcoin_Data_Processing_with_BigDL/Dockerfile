FROM jupyter/pyspark-notebook:python-3.9.13

USER root
WORKDIR /app
COPY . /app

RUN apt-get update && \
    apt-get install -y pandoc && \
    pip install --upgrade pip && \
    pip install wheel setuptools && \
    pip install "pypandoc<1.6" && \
    pip install bigdl-dllib-spark3==2.4.0 && \
    pip install pandas requests matplotlib numpy


EXPOSE 8888
CMD ["bash"]
