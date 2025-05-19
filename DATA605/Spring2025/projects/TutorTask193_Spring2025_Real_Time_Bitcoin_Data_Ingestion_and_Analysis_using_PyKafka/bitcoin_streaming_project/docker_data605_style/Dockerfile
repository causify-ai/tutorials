FROM python:3.11-slim

# Install Java and tools
RUN apt-get update && \
    apt-get install -y default-jre wget curl net-tools unzip gnupg && \
    apt-get clean

# Kafka setup
ENV KAFKA_VERSION=3.6.1
ENV SCALA_VERSION=2.13
ENV KAFKA_HOME=/opt/kafka

RUN wget https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz -O /tmp/kafka.tgz && \
    mkdir -p ${KAFKA_HOME} && \
    tar -xzf /tmp/kafka.tgz --strip-components=1 -C ${KAFKA_HOME} && \
    rm /tmp/kafka.tgz

ENV PATH="${KAFKA_HOME}/bin:${PATH}"

# Working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Make the topic creation script executable
RUN chmod +x /app/kafka_create_topic.sh

# Expose necessary ports
EXPOSE 9092 2181

# Run services and pipeline
CMD ["sh", "-c", "\
    ${KAFKA_HOME}/bin/zookeeper-server-start.sh ${KAFKA_HOME}/config/zookeeper.properties & \
    sleep 5 && \
    ${KAFKA_HOME}/bin/kafka-server-start.sh ${KAFKA_HOME}/config/server.properties & \
    sleep 10 && \
    ./kafka_create_topic.sh && \
    python run.py"]