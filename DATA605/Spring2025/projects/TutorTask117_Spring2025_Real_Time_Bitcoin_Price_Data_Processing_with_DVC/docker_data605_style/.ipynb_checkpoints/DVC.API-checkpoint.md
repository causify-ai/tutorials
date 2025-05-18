
#  bitcoin.API.md  
**Module:** `bitcoin.API.ipynb`  
**Author:** Shruti Gajipara 
**Project:** Real-Time Bitcoin Data Processing with DVC  



## Purpose
This file documents the **low-level API logic and architecture** behind the Bitcoin Price Tracking pipeline. Specifically, it explains what happens **under the hood** — both in terms of the native DVC infrastructure and the custom Python layer built for this project.

---

##  Architecture

The notebook uses the following Python modules:

- `bitcoin_utils.py`: Wrapper around 3 core modules:
  - `src/live_fetcher.py`: Fetches live price via CoinGecko API
  - `src/data_ingestion.py`: Records prices into CSV
  - `src/preprocess_eda.py`: Adds rolling average, computes deltas, plots data

**Core Flow:**
fetch_price() → record_price() → preprocess() → plot_data()


## Native API: DVC (Data Version Control)
The project uses DVC to manage and version the pipeline stages. Under the hood:

### dvc.yaml
Defines pipeline stages:
```yaml
stages:
  fetch_price:
    cmd: python src/fetch_bitcoin_data.py
    deps:
      - src/fetch_bitcoin_data.py
    outs:
      - data/bitcoin_prices.csv

  preprocess_and_plot:
    cmd: python src/preprocess_and_plot.py
    deps:
      - src/preprocess_eda.py
      - data/bitcoin_prices.csv
    outs:
      - data/cleaned_bitcoin.csv
      - Output/bitcoin_price_plot.png
```

###  What Happens:
- DVC checks for changes in dependencies (code or data)
- If changed, it reruns the stage
- Output files are cached and reproducible

### Triggered with:
```bash
dvc repro
```
This runs the pipeline in order, respecting dependencies.

---

##  Custom Python Layer (`bitcoin_utils.py`)
The high-level Python module is the software layer used for:

- Simplifying function calls
- Wrapping business logic (API, preprocessing, plotting)
- Supporting notebook users (clean separation of logic and output)

### Main Functions:
```python
def record_price(filepath="data/bitcoin_prices.csv")
```
- Uses `requests` to query CoinGecko API
- Parses timestamp and price
- Appends row to CSV

```python
def preprocess():
```
- Loads CSV
- Adds `price_diff`, `rolling_avg`
- Returns cleaned DataFrame

```python
def plot_data(df):
```
- Uses matplotlib to plot BTC trend
- Saves to `Output/bitcoin_price_plot.png`

---

##  Notebook-Level Control (`bitcoin.API.ipynb`)
This notebook calls both:

1. Native DVC logic using:
```python
from dvc.repo import Repo
repo = Repo(".")
repo.reproduce()
```
2. High-level wrapper functions:
```python
record_price(), preprocess(), plot_data()
```
3. Visualization and analysis tools:
- Descriptive statistics
- Distribution histograms
- Rolling volatility bands

---

##  Why Two Layers?
| Layer | Purpose |
|-------|---------|
| DVC Pipeline (`dvc.yaml`) | Ensures reproducibility and file versioning |
| Python Utilities (`bitcoin_utils.py`) | Clean abstraction for developers and notebooks |

Combining both enables:
- Reproducible data science pipelines
- Clean separation of config vs logic
- Modular testing and reuse

---

##  Summary
This `.API.md` documents the full stack behavior of the Bitcoin pipeline:
-  DVC for workflow automation and tracking
-  Python modules for logic encapsulation
- Notebooks for easy inspection and experimentation

Everything is versioned, reproducible, and interpretable — satisfying best practices in pipeline design.

##  Dependencies
pandas
requests
matplotlib
dvc

##  Notes

- This notebook is designed to be self-contained.
- All functions are imported from the utils module for cleaner cells.
- API failures (e.g., CoinGecko rate limits) are handled gracefully.
- Final output is suitable for embedding in reports or real-time dashboards.


