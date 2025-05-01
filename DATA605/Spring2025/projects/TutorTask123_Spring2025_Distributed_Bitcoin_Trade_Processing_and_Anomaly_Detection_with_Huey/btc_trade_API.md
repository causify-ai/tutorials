# BTC Trade Processing API (Huey-based Task System)

---

## Introduction

This API provides a distributed task processing system for Bitcoin trade ingestion, aggregation, anomaly detection, and sentiment analysis.  
It is built using **Huey** (a lightweight task queue) with **Redis** as the backend for fault tolerance and **Prometheus** for live monitoring.

The system processes high-frequency Bitcoin trade data, enabling real-time anomaly detection and market sentiment correlation at scale, with robust monitoring and alerting mechanisms.

---

## Technologies Used

- **Huey**: Lightweight task queue for asynchronous, retryable distributed task execution.
- **Redis**: Backend broker ensuring task persistence and durability across worker crashes.
- **Prometheus**: Metrics collection for real-time monitoring of task throughput and performance.
- **Slack API**: Alerts for anomaly detection and task failures.
- **Reddit API (PRAW)**: Fetch Bitcoin subreddit posts for live sentiment analysis.
- **NLTK VADER**: Natural Language Toolkit’s VADER model for sentiment scoring.

---

## Architecture Overview

1. **Real-Time Trade Ingestion**  
   - Bitcoin trades are simulated or streamed.
   - Each trade triggers a Huey task chain asynchronously.

2. **Task Pipeline**  
   - `aggregate_trade`: Aggregates trade prices into 1-minute and 5-minute OHLC (Open, High, Low, Close) buckets.
   - `check_anomaly`: Detects trades that are 3σ outside rolling averages and triggers Slack alerts.
   - `correlate_reddit_sentiment`: Fetches Bitcoin subreddit posts and analyzes their sentiment in parallel.

3. **Fault Tolerance and Retry**  
   - Critical tasks have retries with exponential backoff.
   - Failures after retries trigger Slack notifications.

4. **Monitoring and Alerts**  
   - Task and anomaly metrics are exposed via Prometheus at `http://localhost:8000/metrics`.
   - Grafana dashboards visualize these metrics.
   - Slack is used for critical failure and anomaly alerts.

---

## API Tasks

| Task | Purpose | Retry Mechanism | Prometheus Metrics |
|:-----|:--------|:----------------|:------------------|
| `aggregate_trade(trade)` | Aggregate price into 1-min and 5-min OHLC data. | No retries | No |
| `check_anomaly(trade)` | Detect and alert anomalies beyond 3σ deviation. | 3 retries with exponential backoff | ✅ anomalies_detected_total |
| `correlate_reddit_sentiment(trade)` | Fetch Reddit posts, analyze market sentiment. | 3 retries with exponential backoff | No |
| `process_trade(trade)` | Master task that coordinates aggregation, anomaly check, and sentiment sync. | No retries | ✅ total_trades_processed_total, task_processing_seconds |

---

## Monitoring Metrics

- **`total_trades_processed_total`**: Counter for the total number of trades processed.
- **`anomalies_detected_total`**: Counter for the total number of anomalous trades detected.
- **`task_processing_seconds_count`**: Task execution timing summary for performance tracking.

Metrics can be accessed from Prometheus and visualized on Grafana dashboards.

---

## Fault Handling

- **Automatic Retry**:  
  Tasks like anomaly detection and sentiment analysis retry on failures (e.g., API failures, transient errors) with an exponential backoff strategy.
  
- **Slack Failure Alerts**:  
  If maximum retries are exhausted, a Slack message is sent with the task name and failure reason.

- **Durable Messaging**:  
  Redis backend ensures task messages are not lost during service interruptions.

---

## Usage Flow

1. Start the Redis server container.
2. Launch Huey worker containers.
3. Start the ingestion service to simulate or stream trades.
4. Each trade triggers:
   - Aggregation into OHLC format.
   - Anomaly detection and Slack alerting if thresholds breached.
   - Sentiment analysis based on Reddit's latest posts.
5. Prometheus scrapes metrics for Grafana dashboards.
6. Slack sends real-time alerts on anomalies or task failures.

---

## Example `.env` Variables

```env
SLACK_WEBHOOK=https://hooks.slack.com/services/your/slack/webhook
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=btc-trade-sentiment-bot
