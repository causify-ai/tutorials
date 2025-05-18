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
| `bitcoin_streaming_consumer_emr_debug.py` | Spark job to compute 1-min windowed average from S3 and write to `output/` |
| `bitcoin_kafka/bitcoin_emr_utils.py` | Helper functions for API fetching, timestamping, and S3 upload |
| `bitcoin_emr.API.ipynb` | Demonstrates utility API functions (with simulated S3 upload fallback) |
| `bitcoin_emr.example.ipynb` | Simulates full pipeline with producer input and EMR output |
| `bitcoin_emr.API.md` | Markdown documenting the API and helper layer |
| `bitcoin_emr.example.md` | Markdown documenting the full pipeline example |
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
- Corresponding Markdown Documentation:
  - `bitcoin_emr.API.md`
  - `bitcoin_emr.example.md`

Both notebooks run without requiring cloud setup.

---

## Running the Spark Job on Amazon EMR (Optional)

To run the Spark job (`bitcoin_streaming_consumer_emr_debug.py`) on an actual Amazon EMR cluster and process the real-time Bitcoin data stored in S3:

### 1. Upload Input Data

Ensure the producer script or notebook has pushed data to:

```text
s3://bitcoin-price-streaming-data/data_v2/
```

This folder should contain timestamped `.json` records with the following structure:

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS",
  "price_usd": FLOAT
}
```

---

### 2. Launch and Configure EMR Cluster

Navigate to the [EMR Console](https://console.aws.amazon.com/elasticmapreduce/) and create a cluster with the following configurations:

#### Software Configuration

- **Release version**: EMR 6.x (e.g., 6.13.0)
- **Applications**: Spark (uncheck others if not needed)

#### Hardware Configuration

- **Instance type**: `m5.xlarge` (for both Master and Core)
- **Core nodes**: At least 1
- **Auto-termination**: Enable if needed to save costs

#### General Configuration

- **Cluster name**: `bitcoin-emr-cluster`
- **Logging**: Enable and set an S3 log path (e.g., `s3://your-bucket/emr-logs/`)
- **EC2 key pair**: Select a key pair for SSH access (optional but recommended)

#### Networking

- **VPC**: Use the default or a custom one with public subnet
- **Permissions**:
  - Use a service role with `AmazonS3FullAccess` and `AmazonEMRFullAccessPolicy_v2`
  - Ensure the EC2 instance profile also has access to S3

---

### 3. Submit the Spark Job

You can submit the job in one of two ways:

#### (a) Add a Step from the Console

- Upload `bitcoin_streaming_consumer_emr_debug.py` to S3 (e.g., `s3://your-bucket/scripts/`)
- In the cluster’s "Steps" tab, add a new step:
  - **Type**: Spark
  - **Name**: `Run Bitcoin Streaming Job`
  - **Script location**:
    ```bash
    s3://your-bucket/scripts/bitcoin_streaming_consumer_emr_debug.py
    ```
  - **Arguments**: Leave blank

#### (b) SSH and Run Manually

1. SSH into the master node:
   ```bash
   ssh -i your-key.pem hadoop@<master-node-public-dns>
   ```

2. Run the script using:
   ```bash
   spark-submit      --deploy-mode cluster      --master yarn      s3://your-bucket/scripts/bitcoin_streaming_consumer_emr_debug.py
   ```

---

### 4. Output Location

After execution, check the results in your S3 bucket:

```text
s3://bitcoin-price-streaming-data/output/
```

Each file contains windowed average price data over 1-minute intervals in JSON format.

---

### 📝 Tip

To reduce costs:
- Use **auto-termination** after job completion
- Always **terminate idle clusters**
- Monitor logs in `emr-logs/` for errors or debug output

---

## Summary

- Docker runs the entire project with zero setup  
- AWS and EMR usage is optional but supported  
- Notebooks simulate output if cloud access is unavailable  
- Fully reproducible for grading or real deployment  

---

**Author:** Rithika Baskaran  
**Course:** DATA605 — Spring 2025
