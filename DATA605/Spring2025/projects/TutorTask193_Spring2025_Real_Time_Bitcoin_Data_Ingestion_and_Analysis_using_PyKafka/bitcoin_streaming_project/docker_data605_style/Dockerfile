FROM python:3.11-slim

# Install Java and utilities
RUN apt-get update && \
    apt-get install -y default-jre wget curl net-tools unzip gnupg && \
    apt-get clean

# Kafka setup
# Kafka setup
ENV KAFKA_VERSION=3.6.1
ENV SCALA_VERSION=2.13
ENV KAFKA_HOME=/opt/kafka

RUN wget https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz -O /tmp/kafka.tgz && \
    mkdir -p ${KAFKA_HOME} && \
    tar -xzf /tmp/kafka.tgz --strip-components=1 -C ${KAFKA_HOME} && \
    rm /tmp/kafka.tgz

ENV PATH="${KAFKA_HOME}/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Make scripts executable
RUN chmod +x /app/docker_data605_style/kafka_create_topic.sh

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose ports
EXPOSE 9092 2181

# Run Zookeeper, Kafka, then topic creation and main app
CMD ["sh", "-c", "\
    ${KAFKA_HOME}/bin/zookeeper-server-start.sh ${KAFKA_HOME}/config/zookeeper.properties & \
    sleep 10 && \
    ${KAFKA_HOME}/bin/kafka-server-start.sh ${KAFKA_HOME}/config/server.properties & \
    sleep 15 && \
    ./kafka_create_topic.sh && \
    python run.py"]

