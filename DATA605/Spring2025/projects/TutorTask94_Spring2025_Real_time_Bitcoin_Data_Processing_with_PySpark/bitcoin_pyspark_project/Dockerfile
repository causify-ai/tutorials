FROM jupyter/base-notebook:lab-4.0.5

# Step 1: System setup (Java + Python libs)
USER root
RUN apt-get update && apt-get install -y openjdk-11-jdk curl
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Step 2: Install Python libraries as jovyan
USER $NB_UID
RUN pip install pyspark==3.4.1 requests matplotlib pandas ibm-cos-sdk boto3 

# Step 3: Set working directory and copy project files
WORKDIR /home/jovyan/work

USER root
COPY --chown=jovyan:jovyan work/Data ./Data
RUN chmod -R a+w /home/jovyan/work/Data

COPY --chown=jovyan:jovyan work/bitcoin_utils.py .
COPY --chown=jovyan:jovyan work/run_pipeline.py .


# Step 5: Final run config
USER $NB_UID
CMD ["python", "run_pipeline.py"]
