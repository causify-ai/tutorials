## `Bitcoin_API.ipynb` — Time Series Analysis of Bitcoin Blockchain Metrics

### Purpose of This Notebook

This notebook shows how to fetch Bitcoin blockchain metrics (like transaction count) using a Python function, then apply time series processing and plot the data using Plotly. It is helpful for students learning how to clean real-time financial data, perform basic analysis, and build meaningful visualizations.

---

### What the Notebook Teaches
- How to use a Python function to collect real-time blockchain data  
- How to clean missing values in a time series  
- How to calculate rolling average and Z-scores  
- How to highlight anomalies in data  
- How to visualize the time series using interactive Plotly plots  

---

### Code Explanation

#### 1. Importing Libraries

```python
import pandas as pd  
import numpy as np  
import plotly.graph_objs as go  
import plotly.io as pio  
from statsmodels.tsa.seasonal import seasonal_decompose  
import sys  
sys.path.append('/workspace')  
import template_API as API
```

- `pandas` and `numpy` are used for data manipulation  
- `plotly` is used to build interactive charts  
- `statsmodels` is used for seasonal decomposition  
- `sys.path.append(...)` is used to make sure the `template_API` file can be found and imported  

---

#### 2. Fetch the Bitcoin Metric

```python
df = API.fetch_bitcoin_metric("transaction_count")
df.tail()
```

This line calls the function from the API file and loads 30 days of transaction data into a DataFrame.

---

#### 3. Handle Missing Values and Compute Statistics

```python
df["value"].interpolate(method="linear", inplace=True)  
df["rolling_mean"] = df["value"].rolling(window=10, min_periods=1).mean()  
df["rolling_std"] = df["value"].rolling(window=10, min_periods=1).std()  
df["z_score"] = (df["value"] - df["rolling_mean"]) / df["rolling_std"]
```

- Missing data is filled using linear interpolation  
- Rolling mean and standard deviation are computed to smooth the time series  
- Z-scores are calculated to detect unusual spikes or drops  

---

#### 4. Highlight Anomalies

```python
anomalies = df[df["z_score"].abs() > 2]
```

This filters the DataFrame to keep only the rows where the Z-score is greater than 2 (positive or negative), which helps to find outliers or unusual values.

---

#### 5. Plot with Plotly

```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["value"], mode="lines", name="Value"))
fig.add_trace(go.Scatter(x=df.index, y=df["rolling_mean"], mode="lines", name="Rolling Mean"))
fig.add_trace(go.Scatter(x=anomalies.index, y=anomalies["value"], mode="markers", name="Anomalies", marker=dict(color="red", size=8)))
fig.update_layout(title="Bitcoin Metric with Anomalies", xaxis_title="Date", yaxis_title="Value")
fig.show()
```

This part builds an interactive line plot showing:
- The original Bitcoin metric  
- The rolling average line  
- Red dots for anomaly points detected using Z-score  

---

### Final Thoughts

This notebook is a good beginner-level example of:
- Connecting Python with real blockchain APIs  
- Applying basic statistics on financial data  
- Using Plotly for building useful interactive plots  
- Understanding the behavior of blockchain metrics over time  
