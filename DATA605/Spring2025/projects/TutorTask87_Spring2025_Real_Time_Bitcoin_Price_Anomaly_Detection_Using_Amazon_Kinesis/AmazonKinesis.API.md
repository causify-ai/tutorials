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
