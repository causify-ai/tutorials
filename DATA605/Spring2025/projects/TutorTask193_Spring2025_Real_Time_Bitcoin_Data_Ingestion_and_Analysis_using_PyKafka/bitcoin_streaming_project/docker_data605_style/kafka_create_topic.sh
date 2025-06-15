#!/bin/bash

# Wait for Kafka to fully start
echo "Waiting for Kafka to be ready..."
sleep 5

# Create topic if not exists
echo "Creating Kafka topic: btc-stream"
kafka-topics --create \
  --topic btc-stream \
  --bootstrap-server kafka:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --if-not-exists

echo "Kafka topic 'btc-stream' setup complete."

