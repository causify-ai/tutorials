## `Real_Time_Analysis_Using_PLOTLY.ipynb` — Real-Time Visualization of Bitcoin Blockchain Metrics in a Notebook

### Purpose of This Notebook

This notebook demonstrates how to build a **real-time data visualization tool** using Python and Plotly. It fetches live Bitcoin blockchain metrics like transaction count, block size, and hash rate, and visualizes them with rolling averages, anomaly detection, and seasonal decomposition.

---

### What You Will Learn
- How to collect live blockchain data using an API  
- How to clean and process time series data  
- How to calculate rolling mean, standard deviation, and Z-scores  
- How to perform time series decomposition (trend, seasonal, residual)  
- How to create multi-panel interactive plots using Plotly  
- How to use Python threading for real-time updates in a Jupyter environment  
- How to control the analysis with widgets (buttons, sliders)

---

### Code Structure and Explanation

#### 1. Import Required Libraries

```python
import pandas as pd, numpy as np
import plotly.graph_objs as go, plotly.express as px
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
from datetime import datetime
import time, threading
from IPython.display import display
import ipywidgets as widgets
from template_API import fetch_bitcoin_metric
```

These libraries are used for:
- Data handling and math: `pandas`, `numpy`  
- Plotting: `plotly.graph_objs`, `plotly.subplots`, `plotly.express`  
- Time series analysis: `seasonal_decompose`  
- Real-time handling: `threading`, `time`  
- Widget interface: `ipywidgets`  

---

#### 2. Define `BitcoinMetricsAnalyzer` Class

This class does the full pipeline work:
- Fetches Bitcoin metrics from API  
- Cleans the data (interpolation, rolling mean, z-scores)  
- Performs seasonal decomposition  
- Creates multi-metric visualizations in subplots  
- Detects anomalies and updates the plot live  

---

#### 3. Fetching and Processing Data

```python
fetch_bitcoin_metric(metric)
df["value"].interpolate()
df["rolling_mean"], df["rolling_std"], df["z_score"]
seasonal_decompose(df["value"])
```

Each metric is cleaned and enhanced with additional columns:
- `rolling_mean`: smooths the curve  
- `z_score`: used to find anomalies  
- `trend`, `seasonal`, `residual`: for decomposition  

---

#### 4. Creating Visualizations

```python
make_subplots(...)  
go.Scatter(...)  
go.Heatmap(...)
```

Multiple subplots are created:
- Transaction count, hash rate, block size with their rolling averages  
- Correlation heatmap  
- Trend, seasonal, and residual views  
- Highlighting anomalies where z-score > 2  

---

#### 5. Real-Time Updates

```python
threading.Thread(target=self._update_loop)
```

The notebook supports real-time updates by running a background thread. It fetches new data at fixed intervals and updates the visualization accordingly.

---

#### 6. Interactive Widget Controls

```python
widgets.SelectMultiple, widgets.IntSlider, widgets.Button
```

Widgets are used to:
- Select which metrics to show  
- Adjust update frequency  
- Start and stop the update loop  
- Save the current visualization to HTML  

---

### Final Thoughts

This notebook is a powerful example of how to:
- Combine live API data with advanced visualization  
- Structure Python code with object-oriented programming  
- Build interactive dashboards directly inside a Jupyter environment  

It is ideal for students and analysts interested in cryptocurrency, data visualization, and time series analytics.
