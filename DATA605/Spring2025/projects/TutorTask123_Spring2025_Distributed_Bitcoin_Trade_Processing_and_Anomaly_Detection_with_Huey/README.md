# Distributed Bitcoin Trade Processing & Anomaly Detection with Huey

## Project Overview

This project implements a **distributed Bitcoin trade processing system** using the **Huey task queue**. It ingests **real-time Bitcoin trades** from **Coinbase WebSocket API**, processes and aggregates them, detects **anomalous trades** using the **3-sigma rule**, and **correlates trades with Reddit sentiment**.

The system is designed to:
- Stream **live Bitcoin trades**.
- **Aggregate** 1-min and 5-min **OHLC** (Open-High-Low-Close) data.
- **Detect anomalies** based on historical price distribution.
- **Send Slack alerts** for anomalies.
- **Monitor system health** using Prometheus metrics.
- **Run everything distributedly inside Docker containers**.

---

# Project Structure

```
TutorTask123_btc_trade_huey_pipeline/
├── btc_trade_API.py           # Core trade processing API (Huey tasks, anomaly detection)
├── btc_trade_example.ipynb    # Example notebook to test the API
├── coinbase_stream.py         # WebSocket client to pull live BTC trades
├── README.md                  # Project instructions
├── docker_data605_style/      # Dockerfiles and scripts
│   ├── Dockerfile
│   ├── docker_build.sh
│   ├── docker_bash.sh
│   ├── docker_jupyter.sh
│   ├── requirements.txt
```

---

# Instructions to Run the Project

## Step 1: Clone the Project

```bash
cd ~/src
# Assuming you are already inside the cloned tutorials1 repository
```


## Step 2: Go to Project Folder

```bash
cd DATA605/Spring2025/projects/TutorTask123_btc_trade_huey_pipeline/
```


## Step 3: Build the Docker Image

```bash
cd docker_data605_style
bash docker_build.sh
```

> If bash gives line ending errors, use `dos2unix docker_build.sh` to fix it.

Alternatively (manual build):
```bash
cd ../../
# Run build manually specifying Dockerfile
docker build -t tutortask123/btc_trade_huey_pipeline -f docker_data605_style/Dockerfile .
```


## Step 4: Start Redis Server

```bash
docker run -d --name redis-server -p 6379:6379 redis
```


## Step 5: Start Application Container

```bash
docker run -it --name btc-trade-app -p 8888:8888 -p 8000:8000 -v $(pwd):/app tutortask123/btc_trade_huey_pipeline /bin/bash
```


## Step 6: Install Jupyter Inside the Container (One Time Only)

```bash
pip install jupyter notebook
```


## Step 7: Start Jupyter Server

Inside container:
```bash
jupyter-notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root --NotebookApp.token='' --NotebookApp.password=''
```

Now open in browser:
```plaintext
http://localhost:8888
```


## Step 8: Start Monitoring (Prometheus Metrics)

Prometheus server is auto-started inside the code (`start_monitoring(port=8000)`) when you run the Jupyter notebooks.

Open in browser:
```plaintext
http://localhost:8000/metrics
```

You will see Prometheus metrics like `total_trades_processed`, `anomalies_detected`, etc.


## Step 9: Configure Slack Alerts

Inside the project root, create a `.env` file with:

```
SLACK_WEBHOOK=https://hooks.slack.com/services/XXXXX/XXXXX/XXXXX
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
```

Slack alerts are automatically triggered when anomalous trades are detected.


## Step 10: Stream Live Bitcoin Trades

In a new terminal attached to your running container:

```bash
python coinbase_stream.py
```

This will:
- Connect to Coinbase WebSocket API
- Stream live BTC-USD trades
- Send them to the Huey pipeline

---

# Notes

- **Huey Redis Connection** is configured for Docker networking:
    ```python
    huey = RedisHuey('btc-trade', host='172.17.0.1', port=6379)
    ```

- If you restart the app, ensure that the Redis server (`redis-server` container) is running.

- Anomalous trades are detected using **mean +/- 3\*std**.

- Reddit sentiment is computed using **VADER sentiment** and **PRAW** API.

---

# Useful Commands

| Task                        | Command |
|:-----------------------------|:--------|
| Stop Redis Container         | `docker stop redis-server` |
| Stop App Container           | `docker stop btc-trade-app` |
| Start Redis Again            | `docker start redis-server` |
| Start App Again              | `docker start btc-trade-app` |
| Attach to App Container      | `docker exec -it btc-trade-app /bin/bash` |
| Remove App Container         | `docker rm -f btc-trade-app` |
| Remove Redis Container       | `docker rm -f redis-server` |

---

# Conclusion

✅ After following all the steps, your system will:
- Stream live Bitcoin trades.
- Detect anomalies.
- Send Slack alerts.
- Monitor all activities via Prometheus.
- Run fully in Dockerized distributed environment.

---

> **Done by:** Harshwardhan Singh Rathore, 2025.

> **Course:** DATA605 Spring 2025

---



