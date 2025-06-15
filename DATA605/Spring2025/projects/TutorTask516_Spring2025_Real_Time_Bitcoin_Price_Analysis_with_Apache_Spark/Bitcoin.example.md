
# Bitcoin.example.md

## 📌 Example: Real-Time Bitcoin Price Monitoring and Trend Detection

This example demonstrates a complete application that uses the `fetch_bitcoin_price` wrapper API to build a real-time Bitcoin analytics pipeline. The system performs the following:

- Periodically fetches Bitcoin price data using `fetch_bitcoin_price`
- Writes the data to timestamped CSV files
- Ingests the data using Apache Spark Structured Streaming
- Computes moving averages over configurable time windows
- Detects peaks, valleys, and trends in price behavior
- Visualizes results using Matplotlib

---

## 🐳 Docker-Based Execution (Recommended)

This project runs entirely in a Docker container. To launch the full system:

### 🧪 Build and Run

```bash
./run_in_docker.sh
```

This will:
- Build the Docker image (unless `--skip-build` is passed)
- Launch Jupyter Lab in a container at [http://localhost:8888](http://localhost:8888)
- Mount your current directory inside `/workspace`

### 🧹 Optional Flags

- `--clean`: Removes old Docker image before building
- `--skip-build`: Skips image rebuild (useful if already built)

Example:

```bash
./run_in_docker.sh --clean
```

> ⚠️ macOS users: Ensure your project folder is shared in Docker Desktop > Settings > Resources > File Sharing.

---

## 🧠 Motivation

While the native CoinGecko API allows on-demand price lookup, it lacks:
- Timestamped records
- Retry/error handling
- Real-time integration capability

This wrapper solves these limitations and enables a full analytics workflow.

---

## 🔁 Application Workflow

        +--------------------+
        | CoinGecko API      |
        |  (native endpoint) |
        +--------------------+
                  ↓
    +------------------------------+
    | fetch_bitcoin_price()       |
    | Adds timestamp + retry logic|
    +------------------------------+
                  ↓
    +------------------------------+
    | writer.py                   |
    | Writes real-time CSVs       |
    +------------------------------+
                  ↓
    +------------------------------+
    | Spark Structured Streaming  |
    | Reads + computes averages   |
    +------------------------------+
                  ↓
    +------------------------------+
    | plot.py                     |
    | Visualizes peaks/trends     |
    +------------------------------+

---

## ⚙️ Configurable Parameters

In `bitcoin_utils.py`, the following can be customized:
- **Interval between fetches** (e.g., 15s)
- **Total duration** (e.g., 2 hours)
- **Moving average window sizes** (e.g., 2min, 3min, 5min)
- **Slide interval and watermark for streaming**

---

## 📤 Output Artifacts

- Multiple CSV files (`record_*.csv`) in `data/`
- Moving average results in:
  - `moving_avg_output_{window_size}/`
- Visualization charts:
  - Peak/valley detection using rolling std deviation
  - Trend regions (uptrend/downtrend) annotated with arrows

---

## 📂 Key Files

| File                    | Description                                      |
|-------------------------|--------------------------------------------------|
| `bitcoin_utils.py`      | All functions: writer, Spark stream, analysis    |
| `plot.py`               | Visualizes moving averages, trends, and peaks    |
| `run_in_docker.sh`      | Main script to build + launch in Docker          |
| `Dockerfile`            | Builds the container environment                 |
| `requirements.txt`      | Python dependencies                              |
| `Bitcoin.API.ipynb`     | Notebook showing API and wrapper usage           |
| `Bitcoin.example.ipynb` | Notebook demonstrating full end-to-end example   |

---

## ✅ Summary

This application shows how a simple, robust API wrapper can power a real-time data analytics engine, from ingestion to visualization — all containerized using Docker for reproducibility and portability.
