
#  bitcoin.API.md  
**Module:** `bitcoin.API.ipynb`  
**Author:** Shruti Gajipara 
**Project:** Real-Time Bitcoin Data Processing with DVC  


---
##  Purpose
This markdown documents the usage of both the **native DVC API** and the custom **Python wrapper layer (`bitcoin_utils.py`)** for the Real-Time Bitcoin Data Processing project.

---

##  Architecture

The notebook uses the following Python modules:

- `bitcoin_utils.py`: Wrapper around 3 core modules:
  - `src/live_fetcher.py`: Fetches live price via CoinGecko API
  - `src/data_ingestion.py`: Records prices into CSV
  - `src/preprocess_eda.py`: Adds rolling average, computes deltas, plots data

**Core Flow:**
fetch_price() → record_price() → preprocess() → plot_data()

---

##  Native DVC API (Programmatic Interface)
The notebook demonstrates how to programmatically interact with the DVC project using `dvc.repo.Repo`. It includes:

- **Connecting to the DVC Repo:**
  ```python
  from dvc.repo import Repo
  repo = Repo(".")
  ```

- **Listing DVC Stages (via `dvc.yaml`)**:
  ```python
  import yaml
  with open("dvc.yaml", "r") as file:
      dvc_data = yaml.safe_load(file)
  # Iterates through defined pipeline stages
  ```

- **Programmatically Running the Pipeline:**
  ```python
  repo.reproduce()
  ```
This enables reproducibility and automation of data workflows directly inside the notebook.

---

##  Custom Wrapper API: `bitcoin_utils.py`

The notebook also demonstrates usage of the custom wrapper functions developed in `bitcoin_utils.py`, which abstract various components of the pipeline.

### Core Functions Used:
- `record_price(filepath)`: Records current BTC price from CoinGecko into a CSV.
- `preprocess()`: Adds rolling average, price difference, and returns a cleaned DataFrame.
- `plot_data(df)`: Generates and saves a BTC price plot.

---

##  Visual and Statistical Enhancements
Additional visualizations were added to explore price behavior:

### Plots:
-  Line plot of BTC price over time
- Histogram of BTC prices with mean and median lines
-  Rolling average + volatility band visualization

### Descriptive Stats:
- Summary table for `price`, `price_diff`, `rolling_avg`

### Export:
- Cleaned data is saved as `bitcoin_data_latest.xlsx`

---

##  Output Files Used
| File | Description |
|------|-------------|
| `data/bitcoin_prices.csv` | Raw prices recorded |
| `data/cleaned_bitcoin.csv` | Preprocessed and enriched data |
| `Output/bitcoin_price_plot.png` | Auto-generated chart from `plot_data()` |
| `Output/bitcoin_data_latest.xlsx` | Exported table from cleaned data |

---

##  Summary
This notebook serves as both a testbed and demonstration tool for:
- Native DVC API functionality
- High-level abstraction using a custom software layer
- Data exploration with visual and statistical context

This dual-layer approach makes the system both robust (via DVC) and user-friendly (via `bitcoin_utils.py`).


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


