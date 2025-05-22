FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PRESTO_VERSION=0.278.1
ENV PRESTO_HOME=/opt/presto

RUN apt-get update && apt-get install -y \
    wget openjdk-11-jdk python3 less && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN mkdir -p ${PRESTO_HOME}/plugin/hive /data/hive

WORKDIR ${PRESTO_HOME}

RUN wget -q https://repo1.maven.org/maven2/com/facebook/presto/presto-server/${PRESTO_VERSION}/presto-server-${PRESTO_VERSION}.tar.gz && \
    tar -xzf presto-server-${PRESTO_VERSION}.tar.gz --strip-components=1 && \
    rm presto-server-${PRESTO_VERSION}.tar.gz

RUN wget -q https://repo1.maven.org/maven2/com/facebook/presto/presto-hive/${PRESTO_VERSION}/presto-hive-${PRESTO_VERSION}.jar \
    -O ${PRESTO_HOME}/plugin/hive/presto-hive-${PRESTO_VERSION}.jar

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir pandas requests matplotlib pyarrow jupyter

# Expose Jupyter Notebook port
EXPOSE 8080

# Run Jupyter Notebook by default
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8080", "--no-browser", "--allow-root"]
