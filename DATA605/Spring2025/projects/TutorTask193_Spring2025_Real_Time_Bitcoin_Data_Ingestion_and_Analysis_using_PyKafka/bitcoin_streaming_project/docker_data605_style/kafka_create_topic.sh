#!/bin/bash

KAFKA_HOME=/opt/kafka
TOPIC_NAME=bitcoin_price
BROKER=localhost:9092

# Create the topic if it doesn't already exist
$KAFKA_HOME/bin/kafka-topics.sh \
  --create \
  --if-not-exists \
  --topic $TOPIC_NAME \
  --bootstrap-server $BROKER \
  --replication-factor 1 \
  --partitions 1

# Confirm the topic exists
$KAFKA_HOME/bin/kafka-topics.sh --list --bootstrap-server $BROKER