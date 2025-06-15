## `Real_Time_Analysis_Using_PLOTLY.py` — Real-Time Visualization of Bitcoin Blockchain Metrics

### Purpose of This File

This script collects, processes, and visualizes multiple real-time Bitcoin blockchain metrics such as transaction count, hash rate, and block size. It uses a class-based structure to organize the code and Plotly for interactive visualization. It also supports real-time updates and saving the visual output to HTML. This file is useful for students who want to learn how to build real-time dashboards and time series visualizations using Python.

---

### What the Code Teaches
- How to use threading to fetch data in real-time  
- How to organize code using Python classes  
- How to apply rolling statistics and seasonal decomposition  
- How to use Plotly for multi-panel subplots and anomaly detection  
- How to build interactive dashboards with Jupyter widgets  

---

### Code Explanation

#### 1. Import Libraries

```python
import pandas as pd  
import numpy as np  
import plotly.graph_objs as go  
from plotly.subplots import make_subplots  
from statsmodels.tsa.seasonal import seasonal_decompose  
from datetime import datetime, timedelta  
import time  
import threading  
from IPython.display import display  
import ipywidgets as widgets  
from template_API import fetch_bitcoin_metric
```

This block loads the tools for:
- Data handling and calculations (`pandas`, `numpy`)  
- Plotting (`plotly`)  
- Time series decomposition (`seasonal_decompose`)  
- Real-time updates (`time`, `threading`)  
- Jupyter-based interactivity (`ipywidgets`, `display`)  
- Data fetching from an external script (`fetch_bitcoin_metric`)  

---

#### 2. Class: `BitcoinMetricsAnalyzer`

This class encapsulates all the logic needed for:
- Collecting data from multiple metrics  
- Processing data (rolling mean, z-score, decomposition)  
- Visualizing in a subplot format  
- Running real-time updates  
- Saving plots to HTML  

---

#### 3. `fetch_all_metrics()` Method

```python
def fetch_all_metrics(self):
    ...
```

Fetches data for all three metrics and updates internal data storage (`df_dict`). Also calls a private method `_process_metric()` to clean and prepare each dataset.

---

#### 4. `_process_metric()` Method

```python
def _process_metric(self, metric):
    ...
```

This performs:
- Linear interpolation to handle missing data  
- Rolling mean and standard deviation  
- Z-score calculation  
- Seasonal decomposition into trend, seasonal, and residual components  

---

#### 5. `create_visualization()` Method

```python
def create_visualization(self):
    ...
```

This builds a complex, interactive Plotly figure with multiple rows:
- Time series plots of each metric  
- Rolling means overlaid on each plot  
- Correlation heatmap  
- Seasonal decomposition (trend, seasonal, residual)  
- Anomaly detection (z-score > 2 highlighted with markers)  
- Rangeslider and time-based filters (1h, 1d, 1w, All)  

---

#### 6. Real-Time Update Handling

```python
def start_real_time_updates(self):
def stop_real_time_updates(self):
def _update_loop(self):
```

These methods handle continuous background fetching using threading. The `_update_loop` repeatedly calls `fetch_all_metrics()` and updates the visualization at intervals defined by `update_interval`.

---

#### 7. Saving Output to HTML

```python
def save_to_html(self, filename=None):
    ...
```

Exports the current visualization to a standalone HTML file with the current timestamp.

---

#### 8. Jupyter Widget Interface

```python
def create_jupyter_widgets(analyzer):
    ...
```

Creates interactive dropdowns, sliders, and buttons in Jupyter to:
- Select metrics  
- Adjust update frequency  
- Start/Stop real-time updates  
- Save the plot to HTML  

---

#### 9. `main()` Function

```python
def main():
    ...
```

This is the entry point for running the script directly. It:
- Instantiates the class  
- Fetches data  
- Creates and displays the figure  
- Starts the real-time update loop  

---

### Final Thoughts

This file is a complete example of building a **real-time, multi-metric data visualization tool**. It is ideal for:
- Students learning about time series analysis  
- Building dashboards with Python and Plotly  
- Working with real blockchain data  
- Implementing interactive features using Jupyter widgets and threading  
