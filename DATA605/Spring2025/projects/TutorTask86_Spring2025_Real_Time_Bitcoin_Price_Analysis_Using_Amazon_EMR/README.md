# Real-Time Bitcoin Price Analysis Using Amazon EMR

This project demonstrates a real-time data processing pipeline that collects Bitcoin price data from a public API, stores it in Amazon S3, and processes it using Apache Spark on Amazon EMR for time-series analysis.

---

## Technologies Used

- **CoinGecko API** – Fetching live Bitcoin price in USD  
- **Python** – Core scripting language  
- **Boto3** – AWS SDK to interact with Amazon S3  
- **Amazon S3** – For storing raw and processed data  
- **Apache Spark (Structured Streaming)** – For 1-minute windowed aggregation  
- **Amazon EMR** – Cluster to run Spark jobs at scale  
- **Docker** – Containerized environment for portability and reproducibility  

---

## Project Structure

| File/Folder | Description |
|-------------|-------------|
| `bitcoin_producer.py` | Fetches real-time Bitcoin prices and writes records to S3 (`data_v2/`) |
| `bitcoin_streaming_consumer_emr_debug.py` | Spark job to compute 1-min windowed average from S3 and write to `output_streaming/` |
| `bitcoin_kafka/bitcoin_emr_utils.py` | Helper functions for API fetching, timestamping, and S3 upload |
| `bitcoin_emr.API.ipynb` | Demonstrates utility API functions (with simulated S3 upload fallback) |
| `bitcoin_emr.example.ipynb` | Simulates full pipeline with producer input and EMR output |
| `requirements.txt` | Python package requirements |
| `Dockerfile` + `*.sh` | Docker setup and run scripts |

---

## Output Format

### Input Record (stored in S3)

```json
{
  "timestamp": "2025-05-17T09:58:00",
  "price_usd": 102723.12
}
```

### Processed Output (via Spark on EMR)

```json
{
  "window": {
    "start": "2025-05-17T09:58:00",
    "end": "2025-05-17T09:59:00"
  },
  "avg_price": 102750.13
}
```

---

## AWS Credentials Note

This project uses `boto3` to upload Bitcoin price records to Amazon S3.

If valid AWS credentials are present, records will be uploaded to:

```text
s3://bitcoin-price-streaming-data/data_v2/
```

⚠️ If credentials are not present, the upload will be skipped gracefully, and the JSON record will be printed instead.

This ensures the notebooks run end-to-end even without AWS setup.

---

## Docker Setup Instructions

You can run this project entirely in Docker without installing any local dependencies.

### To Build the Image

```bash
bash docker_build.sh
```

### To Run the Container

```bash
bash docker_bash.sh
```

### Open Jupyter

Once the container is running, open your browser and go to:

```text
http://localhost:8888
```

---

### Notebooks to Run

- `bitcoin_emr.API.ipynb` – Test API functions, simulate S3 upload  
- `bitcoin_emr.example.ipynb` – Simulate full pipeline input + output  

Both run without requiring cloud setup.

---

## Running the Spark Job on Amazon EMR (Optional)

To run the Spark job (`bitcoin_streaming_consumer_emr_debug.py`) on an actual EMR cluster:

### 1. Set Up Input Data

Ensure input records are stored at:

```text
s3://bitcoin-price-streaming-data/data_v2/
```

### 2. Launch EMR Cluster

- EMR version: **6.x**  
- Applications: **Spark**  
- Instance type: `m5.xlarge` or similar

### 3. Submit Spark Job

Upload the script to the cluster or S3 and run:

```bash
spark-submit   --deploy-mode cluster   --master yarn   bitcoin_streaming_consumer_emr_debug.py
```

### 4. Output Location

Results will be written to:

```text
s3://bitcoin-price-streaming-data/output_streaming/
```

---

## Summary

- Docker runs the entire project with zero setup  
- AWS and EMR usage is optional but supported  
- Notebooks simulate output if cloud access is unavailable  
- Fully reproducible for grading or real deployment  

---

**Author:** Rithika Baskaran  
**Course:** DATA605 — Spring 2025
