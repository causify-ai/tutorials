
# 🪙 Real-Time Bitcoin Price Analysis with Apache Spark

This project demonstrates a real-time streaming pipeline for monitoring and analyzing Bitcoin prices using:

- ✅ **CoinGecko API** for real-time price data
- ✅ **Apache Spark Structured Streaming** for moving averages
- ✅ **Python multiprocessing** to run ingestion + processing in parallel
- ✅ **Matplotlib** to visualize peaks, valleys, and trends
- ✅ **Docker** to containerize the full pipeline and Jupyter environment

---

## 🧱 Project Structure

```
bitcoin_project/
├── bitcoin_utils.py          # All logic for data collection, Spark setup, and analysis
├── plot.py                   # Visualization of moving averages, peaks, and trends
├── Bitcoin.API.ipynb         # API demo: native + wrapped usage
├── Bitcoin.example.ipynb     # End-to-end pipeline demo
├── requirements.txt          # Python dependencies
├── run_in_docker.sh          # One-step Docker launch script
├── run_jupyter.sh            # Entrypoint for Jupyter Lab
├── docker/
│   ├── Dockerfile            # Docker image definition
│   ├── docker_build.sh       # Builds Docker image
│   ├── docker_jupyter.sh     # Launches Jupyter Lab in container
│   └── docker_clean.sh       # Cleans idle containers and prunes all images (optional)
├── Bitcoin.API.md            # Markdown: API documentation
├── Bitcoin.example.md        # Markdown: application example
└── data/, moving_avg_output/ # Generated outputs
```

---

## 🐳 Docker Setup

All Docker logic is encapsulated in `run_in_docker.sh`.

### 🔧 Build and Run

```bash
./run_in_docker.sh
```

### 🧹 Optional Flags

- `--clean`       Remove previous Docker image before building
- `--skip-build`  Skip rebuild (launch container directly)

Example:

```bash
./run_in_docker.sh --clean
```

- Opens Jupyter Lab at [http://localhost:8888](http://localhost:8888)
- Mounts your project into the container at `/workspace`

---

## ⚙️ Notebooks

| Notebook                | Description                                  |
|-------------------------|----------------------------------------------|
| `Bitcoin.API.ipynb`     | Shows native vs. wrapped API usage           |
| `Bitcoin.example.ipynb` | Full pipeline: write → stream → plot         |

---

## 📊 Visualizations

Run:

```python
# Inside the notebook or Jupyter terminal
!python plot.py
```

- Highlights peaks/valleys using rolling 5-point extrema
- Shades trend regions using adaptive thresholds
- Supports multiple window size overlays

---

## ✅ Cleanup

```bash
docker rm -f $(docker ps -aq)
docker rmi -f bitcoin_project
docker system prune -f
```

---

## 📚 References

- [CoinGecko API Docs](https://www.coingecko.com/en/api/documentation)
- Apache Spark Structured Streaming
- Matplotlib, Pandas, PySpark
