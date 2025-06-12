# Real-Time Bitcoin Price Analysis Example

<!-- toc -->

- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Workflow Steps](#workflow-steps)
  - [1. Environment Setup](#1-environment-setup)
  - [2. CSV Initialization](#2-csv-initialization)
  - [3. Demo ETL with Petl](#3-demo-etl-with-petl)
  - [4. Continuous Ingestion](#4-continuous-ingestion)
  - [5. Time-Series Analysis](#5-time-series-analysis)
  - [6. Static Visualizations](#6-static-visualizations)
  - [7. Seasonal Decomposition](#7-seasonal-decomposition)
  - [8. Interactive Dashboard](#8-interactive-dashboard)
- [How to Run](#how-to-run)
- [General Guidelines](#general-guidelines)

<!-- tocstop -->

## Project Overview

This tutorial notebook (`BitcoinPetl.example.ipynb`) demonstrates a complete, end-to-end pipeline for:

1. Fetching live BTC price data  
2. Performing ETL transformations with Petl  
3. Conducting time series analysis in pandas  
4. Visualizing results statically and interactively  

## Prerequisites

- Python libraries: `petl`, `requests`, `pandas`, `matplotlib`, `seaborn`, `statsmodels`, `plotly`  
- Docker environment set up via `docker_common/docker_build.sh`

## Workflow Steps

### 1. Environment Setup

Install and import dependencies:

```bash
pip install petl requests pandas matplotlib seaborn statsmodels plotly
```

```python
import os, time
from datetime import datetime, timedelta
import petl as etl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import plotly.graph_objects as go
from IPython.display import clear_output

from bitcoin_petl_utils import (
    init_csv, append_price, fetch_btc_price_table,
    expand_demo_rows, filter_recent, load_dataframe,
    add_indicators, fetch_historical_range
)
```

### 2. CSV Initialization

Create/reset the CSV file:

```python
init_csv("btc_prices.csv")
```

### 3. Demo ETL with Petl

Generate and transform a 5-row demo table:

```python
demo = expand_demo_rows(fetch_btc_price_table(), n=5, dt=60)
converted = (
    demo
    .convert('timestamp', lambda t: datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S'))
    .convert('price_usd', float)
    .rename('price_usd', 'price_usd_float')
    .sort('price_usd_float', reverse=True)
)
print(etl.look(converted))
```

### 4. Continuous Ingestion

Append live data every 30 seconds:

```python
for _ in range(10):
    append_price("btc_prices.csv")
    time.sleep(30)
```

### 5. Time-Series Analysis

Load into pandas and compute indicators:

```python
df = load_dataframe("btc_prices.csv")
df = add_indicators(df, window=3)
df.head()
```

### 6. Static Visualizations

Plot price and moving average:

```python
plt.figure(figsize=(10,4))
plt.plot(df.index, df["price_usd"], label="Price")
plt.plot(df.index, df["MA_3"], label="MA (3)")
plt.legend(); plt.show()
```

Plot rolling volatility:

```python
sns.lineplot(data=df.reset_index(), x="timestamp", y="VOL_3")
plt.show()
```

### 7. Seasonal Decomposition

```python
from statsmodels.tsa.seasonal import seasonal_decompose
decomp = seasonal_decompose(df["price_usd"].dropna(), period=3, model="additive", two_sided=False)
decomp.plot(); plt.show()
```

### 8. Interactive Dashboard

Fetch last 7 days trailing by 3 minutes, compute MA(10), and display:

```python
# inside a loop with clear_output and fig.show(renderer="notebook")
```

## How to Run

1. Build & launch Docker:
   ```bash
   bash docker_common/docker_build.sh
   bash docker_common/docker_bash.sh
   ```
2. In Jupyter, **Restart & Run All** on both notebooks.  
3. Interrupt the live cell when finished.