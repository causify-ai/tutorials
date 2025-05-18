#!/bin/bash

# entrypoint.sh
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
export PATH=$JAVA_HOME/bin:$PATH

# 1. Wait for Kafka to be ready
echo " Waiting for Kafka to start..."
sleep 15

# 2. Clean previous output
echo " Cleaning old output..."
rm -rf /workspace/output/*

# 3. Start Producer in background
echo " Starting Kafka producer..."
python3 /workspace/kafka_producer_example.py &

# 4. Start Spark consumer
echo " Launching Spark consumer (this will block)..."
python3 /workspace/spark_consumer_example.py &

# 5. Wait a bit for data to be generated
sleep 30

# 6. Show output directory contents
echo " Listing Parquet output files:"
find /workspace/output -type f -name '*.parquet'

# 7. Keep container alive
tail -f /dev/null
