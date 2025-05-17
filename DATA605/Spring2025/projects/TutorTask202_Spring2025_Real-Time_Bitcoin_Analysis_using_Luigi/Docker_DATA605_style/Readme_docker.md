# Docker Integration – Coingecko Bitcoin Analytics Pipeline

This project is Docker-integrated using the provided `docker_data605_style` setup. The pipeline fetches BTC-USD data from the Coingecko API and processes it using Luigi.

---

## Folder Structure

```
bitcoin_price/
├── coingecko_utils.py              # API wrapper + 6 Luigi tasks
├── coingecko.API.ipynb             # Native API usage demo
├── coingecko.example.ipynb         # Full pipeline execution notebook
├── Dockerfile                      # Image configuration
├── README_docker.md                # This file
├── requirements.txt                # Python packages
├── data/                           # Outputs
└── docker_data605_style/           # Container utilities
```

---

## Step 1: Build Docker Image

```bash
cd docker_data605_style
./docker_build.sh
```

---

## Step 2: Run the Container

### Open Bash shell in container

```bash
./docker_bash.sh
```

Then run:

```bash
export $(cat .env | xargs)
python -m luigi --module coingecko_utils StoreToS3Task --local-scheduler
```

---

### Or launch Jupyter:

```bash
./docker_jupyter.sh -p 8889
```

Visit: [http://localhost:8889](http://localhost:8889)

---

## Output Files

| Task                | Output                         |
|---------------------|--------------------------------|
| FetchDataTask       | `data/raw_<date>.json`         |
| CleanDataTask       | `data/clean_<date>.csv`        |
| AnalyzeDataTask     | `data/analyzed_<date>.csv`     |
| VisualizeDataTask   | `data/plot_<date>.png`         |
| AlertTask           | `data/alert_<date>.txt` + email |
| StoreToS3Task       | Uploaded to S3                 |

---

## Notes

- Make sure `.env` is configured
- `requirements.txt` ensures all Python dependencies are preinstalled