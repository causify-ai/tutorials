# Amazon Kinesis & Apache Flink - API Tutorial

<!-- toc -->

- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
- [Setting Up](#setting-up)
  * [Dependencies](#dependencies)
- [Amazon Kinesis](#amazon-kinesis)
  * [Stream Creation](#stream-creation)
  * [Producing Data](#producing-data)
- [Apache Flink (Managed Service)](#apache-flink-managed-service)
  * [Application Setup](#application-setup)
  * [Example Use Case](#example-use-case)
- [Amazon S3](#amazon-s3)
  * [Sink Integration](#sink-integration)
- [Usage in This Project](#usage-in-this-project)

<!-- tocstop -->

## Introduction

This tutorial introduces the key AWS streaming technologies used to build real-time data processing pipelines: **Amazon Kinesis**, **Apache Flink (Managed Service)**, and **Amazon S3**. These services are widely used in streaming analytics, fraud detection, and financial monitoring.

By the end of this tutorial, you’ll understand how to:

- Create and work with Kinesis Data Streams.
- Build real-time stream processors using Flink.
- Configure S3 as a reliable sink for streaming outputs.
- Connect these services to build a scalable pipeline.

---

## Architecture Overview

The architecture includes:

- **Amazon Kinesis**: For ingesting high-throughput streaming data (e.g., market feeds).
- **Apache Flink (via AWS Managed Service)**: For low-latency stream processing.
- **Amazon S3**: For durable and scalable output storage.

![architecture diagram placeholder](figures/kinesis-flink-s3.png)

These services can be used individually or integrated together into powerful streaming applications.

---

## Setting Up

### Dependencies

To follow along, you'll need:

- An AWS account
- AWS CLI configured (`aws configure`)
- IAM permissions to create Kinesis, S3, and Flink resources
- (Optional) Python 3 and `boto3` for local stream producers

---

## Amazon Kinesis

Amazon Kinesis is a fully managed service for real-time data streaming.

You can use **Kinesis Data Streams** to ingest and buffer high-frequency data like trading prices, logs, or IoT signals.

### Stream Creation

You can create a stream from the AWS console or CLI:

```bash
aws kinesis create-stream --stream-name btc-stream --shard-count 1
```
### Producing Data

Data can be produced using the AWS SDK:

```python
import boto3
import json

client = boto3.client("kinesis")

data = {
    "timestamp": "2025-04-30T12:00:00Z",
    "price": 63800.5,
    "volume": 0.25
}

client.put_record(
    StreamName="btc-stream",
    Data=json.dumps(data),
    PartitionKey="btc"
)
```

## Apache Flink (Managed Service)

Apache Flink is a powerful open-source framework for stateful stream processing. AWS provides a **managed service** that eliminates the complexity of infrastructure setup.

### Application Setup

1. Go to **Kinesis Data Analytics → Apache Flink**.
2. Click **Create Application**.
3. Upload a **JAR file** containing your Flink job.
4. Assign the required **IAM role**.
5. Define:
   - Source: your Kinesis Data Stream (e.g., `btc-stream`)
   - Sink: S3 or another Kinesis stream
   - Parallelism and Flink configuration

### Example Use Case

A common Flink job might:
- Read from a Kinesis stream.
- Apply windowing logic to compute a rolling average.
- Compare the latest value to the rolling statistics.
- Flag anomalies that deviate beyond 3σ (standard deviations).

Flink offers time-based windows (`Time.minutes(1)`), key-based partitioning, and native integration with AWS Kinesis connectors.


## Amazon S3

Amazon S3 is a highly durable, scalable object store. It’s often used as a sink in streaming jobs for archiving processed outputs or anomaly flags.

### Sink Integration

Flink provides `StreamingFileSink`:

```java
StreamingFileSink<String> s3Sink = StreamingFileSink
    .forRowFormat(new Path("s3://your-bucket/your-prefix/"),
        new SimpleStringEncoder<String>("UTF-8"))
    .build();

anomalies.addSink(s3Sink);
```

Flink will handle batching, file rolling, and delivery guarantees when writing to S3.

To enable Flink → S3 writes:

- Attach s3:PutObject permissions to your application role.

- Enable checkpointing in Flink for better durability.

## Usage in This Project

We use these services together as follows:

- **Kinesis** streams real-time Bitcoin price and volume data.
- **Flink**, deployed via the Managed Service, processes this data:
  - Applies 1-minute tumbling windows.
  - Flags outliers where price deviates > 3σ (standard deviations).
- **S3** stores the flagged anomalies in JSON format for inspection or downstream analytics.

This architecture is scalable, cloud-native, and ideal for real-time anomaly detection in financial data or IoT monitoring.
