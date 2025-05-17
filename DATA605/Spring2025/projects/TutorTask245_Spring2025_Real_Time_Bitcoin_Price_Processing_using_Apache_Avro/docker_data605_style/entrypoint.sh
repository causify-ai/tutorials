#!/bin/bash

# 1. Wait for Kafka to be ready
echo " Waiting for Kafka to start..."
sleep 15

# 2. Create Kafka topic (if not exists)
echo " Creating Kafka topic: bitcoin_prices"
kafka-topics --create --if-not-exists --bootstrap-server host.docker.internal:9093 --replication-factor 1 --partitions 1 --topic bitcoin_prices

# 3. Clean previous output
echo " Cleaning old output..."
rm -rf /workspace/output/*

# 4. Start Producer in background
echo " Starting Kafka producer..."
python3 /workspace/kafka_producer.py &

# 5. Start Spark consumer
echo " Launching Spark consumer (this will block)..."
python3 /workspace/spark_consumer.py &

# 6. Wait a bit for data to be generated
sleep 30

# 7. Show output directory contents
echo " Listing Parquet output files:"
find /workspace/output -type f -name '*.parquet'

# 8. Keep container alive
tail -f /dev/null
