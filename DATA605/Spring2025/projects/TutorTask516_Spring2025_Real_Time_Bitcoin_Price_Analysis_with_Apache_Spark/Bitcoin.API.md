
# Bitcoin.API.md

## 1. Native API: CoinGecko

### API Endpoint
https://api.coingecko.com/api/v3/simple/price

### Query Parameters
| Parameter        | Description                             | Example                      |
|------------------|-----------------------------------------|------------------------------|
| `ids`            | The cryptocurrency ID                   | `bitcoin`                    |
| `vs_currencies`  | The fiat currency for conversion        | `usd`                        |

### Sample Request
GET https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd

### Sample Response
```json
{
  "bitcoin": {
    "usd": 103765.27
  }
}
```

### Limitations
- No timestamp in response
- Rate limited
- No built-in retry logic

---

## 2. Wrapper Layer: fetch_bitcoin_price

### File Location
`bitcoin_utils.py`

### Function Signature
```python
fetch_bitcoin_price(max_retries=5, base_delay=2, verbose=True)
```

### Features
- Adds a timestamp using the system clock
- Handles request failures and API rate limits
- Implements exponential backoff (2, 4, 8... seconds)
- Easy-to-use dictionary output for streaming pipelines
- Optional verbose logging for monitoring

---

## 🐳 Docker Environment

This API wrapper is designed to run inside a containerized environment using Docker.

### 🔧 Build the Docker Image

Run this from the root of the project:

```bash
./run_in_docker.sh
```

This script will:
- Build the Docker image (unless `--skip-build` is passed)
- Launch Jupyter Lab at [http://localhost:8888](http://localhost:8888)

> ⚠️ macOS users: Make sure to allow your folder in Docker Desktop > Settings > Resources > File Sharing.

### ✅ Example Usage Inside Notebook

```python
from bitcoin_utils import fetch_bitcoin_price

record = fetch_bitcoin_price()
print(record)
```

Expected output:
```python
{
  'timestamp': '2025-05-18T13:05:43.612825',
  'price': 103765.27
}
```

---

## 🧪 Related Notebook

- `Bitcoin.API.ipynb` — demonstrates both raw API access and the wrapper function

---

## ✅ Summary

Wrapping a public API with retry logic and timestamp enrichment makes it suitable for real-time pipelines. This implementation enables robust ingestion of live Bitcoin pricing data inside a scalable streaming workflow.
