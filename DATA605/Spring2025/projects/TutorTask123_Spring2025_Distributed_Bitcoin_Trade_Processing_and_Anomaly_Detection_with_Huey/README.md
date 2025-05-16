# Distributed Bitcoin Trade Processing & Anomaly Detection with Huey

## Project Overview

This project implements a **distributed Bitcoin trade processing system** using the **Huey task queue**. It ingests **real-time Bitcoin trades** from **Coinbase WebSocket API**, processes and aggregates them, detects **anomalous trades** using the **3-sigma rule**, and **correlates trades with Reddit sentiment**.

The system is designed to:
- Stream **live Bitcoin trades**.
- **Aggregate** 1-min and 5-min **OHLC** (Open-High-Low-Close) data.
- **Detect anomalies** based on historical price distribution.
- **Send Slack alerts** for anomalies.
- **Monitor system health** using Prometheus metrics.
- **Run everything distributedly inside Docker containers with Docker Compose**.

## Project Structure

```
TutorTask123_btc_trade_huey_pipeline/
├── btc_trade_API.py
├── btc_trade_tasks.py
├── coinbase_stream.py
├── btc_trade_utils.py
├── anomaly.py
├── docker-compose.yml
├── docker_data605_style/
│   ├── Dockerfile
│   ├── requirements.txt
├── README.md
```

## How to Run the Entire Project (Recommended)

### For both **Windows and Mac/Linux users**

#### Step 1: Clone and navigate to the project

```bash
cd <your_project_directory>
```

#### Step 2: Create `.env` file in the project root

```
SLACK_WEBHOOK=https://hooks.slack.com/services/XXXXX/XXXXX/XXXXX
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
```

#### Step 3: Run everything in one command using Docker Compose

##### For Windows:
```bash
docker-compose up --build
```

##### For Mac/Linux:
```bash
docker-compose up --build
```

> This will:
> - Build the Docker image.
> - Start Redis container.
> - Start Huey consumer + Coinbase Stream producer inside `btc_pipeline_app`.
> - Expose Prometheus metrics on `http://localhost:8000/metrics`.

## Additional Launcher Scripts (Optional)

### For Windows Users (`run_pipeline.bat`)
```bat
@echo off
docker-compose down --volumes --remove-orphans
docker-compose build --no-cache
docker-compose up
pause
```

### For Mac/Linux Users (`run_pipeline.sh`)
```bash
#!/bin/bash
docker-compose down --volumes --remove-orphans
docker-compose build --no-cache
docker-compose up
```

Make executable:
```bash
chmod +x run_pipeline.sh
```

Run:
```bash
./run_pipeline.sh
```

## Monitoring

- Prometheus metrics at:  
  ```plaintext
  http://localhost:8000/metrics
  ```

- Metrics include:
  - `total_trades_processed`
  - `anomalies_detected`
  - Task processing times

## Slack Alerts

Ensure your `.env` file has the correct Slack webhook.  
Alerts are triggered automatically when anomalies are detected.

## Conclusion

 The whole pipeline will run **fully distributed inside Docker Compose**.  
No need to run anything manually inside containers.

> **Done by:** Harshwardhan Singh Rathore, 2025.
> 
> **Course:** DATA605 Spring 2025