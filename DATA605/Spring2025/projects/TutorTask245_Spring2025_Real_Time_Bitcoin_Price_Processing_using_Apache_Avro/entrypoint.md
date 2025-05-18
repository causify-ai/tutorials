<!-- toc -->

- [Introduction](#introduction)
  * [Key Steps](#key-steps)
    + [1. Environment Setup](#1-environment-setup)
    + [2. Kafka Readiness and Cleanup](#2-kafka-readiness-and-cleanup)
    + [3. Launching the Kafka Producer](#3-launching-the-kafka-producer)
    + [4. Launching the Spark Consumer](#4-launching-the-spark-consumer)
    + [5. Listing Output Files](#5-listing-output-files)
    + [6. Container Persistence](#6-container-persistence)
  * [Complete Workflow](#complete-workflow)
  * [Example Output](#example-output)

<!-- tocstop -->

# Introduction

This script (`entrypoint.sh`) orchestrates the entire Bitcoin streaming data pipeline. It performs environment setup, launches the Kafka producer and Spark consumer, lists the Parquet outputs, and keeps the container alive for continuous streaming.

## Key Steps

### 1. Environment Setup

Sets up the `JAVA_HOME` and appends it to `PATH` to ensure PySpark can find the correct JVM.

```bash
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
export PATH=$JAVA_HOME/bin:$PATH

```

## 2. Kafka Readiness and Cleanup

 Waits for Kafka services to start and clears any previous output from the workspace directory.




## 3. Launching the Kafka Producer

Starts the kafka_producer.py script in the background, which continuously fetches Bitcoin price data and sends it to the Kafka topic bitcoin_prices.



## 4. Launching the Spark Consumer

 Runs the spark_consumer.py script, which reads from Kafka, performs real-time analytics (moving average and volatility), and writes the results to Parquet.


## 5. Listing Output Files

After giving some time for Spark to write the outputs, lists all Parquet files generated under the /workspace/output/ directory.



## 6. Container Persistence

Keeps the Docker container alive so that the streaming job remains active indefinitely.


## Process FlowChart

<img src="https://github.com/user-attachments/assets/fcda0cd9-f7d4-41fd-97c7-5a0e5f8386d9" width="500"/>



## Example Output

```
 Waiting for Kafka to start...
 Cleaning old output...
 Starting Kafka producer...
 Launching Spark consumer (this will block)...
 Listing Parquet output files:
/workspace/output/bitcoin_price_avg/part-00000-*.parquet
/workspace/output/bitcoin_volatility/part-00000-*.parquet

```
