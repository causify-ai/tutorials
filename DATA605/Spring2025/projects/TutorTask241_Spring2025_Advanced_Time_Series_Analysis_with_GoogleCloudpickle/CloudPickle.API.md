Advanced Time Series Analysis with Google Cloudpickle
=======================================

This document provides a comprehensive overview of:

-   The **native CoinGecko API** used for fetching Bitcoin price data.

-   The **native `cloudpickle`** Python API for serializing complex objects and code.

-   The **custom wrapper** layer (`CloudPickle_utils.py`) built on top of both.

* * * * *

1\. Native CoinGecko API
------------------------

**API Name:** CoinGecko Public API\
**Endpoint Used:** `/coins/{id}/market_chart`\
**Purpose:** Fetch historical market data (price, market cap, 24h volume) for a coin.\
**Data Format:** JSON

**Key Parameters:**

-   `vs_currency` (string, required): Target currency (`usd`, `eur`, `jpy`, etc.).

-   `days` (string or int, required): Number of past days.

    -   `1` → returns **hourly** data for last 24 h.

    -   `2--90` → returns **daily** data.

    -   `>90` → daily data by default.

**Rate Limiting & Authentication:**

-   Public endpoints are free but rate-limited (≈ 5--10 calls/minute/IP).

-   For higher volumes, register for an API key and include it in headers.

**Example Response (prices snippet):**

```
{
  "prices": [
    [1678886400000, 24500.50],
    [1678890000000, 24550.75]
  ],
  "market_caps": [...],
  "total_volumes": [...]
}

```

* * * * *

2\. Native `cloudpickle` API
----------------------------

The `cloudpickle` library extends Python's built-in `pickle` module, enabling serialization of a **wider range of Python objects**. It is essential in distributed computing, remote execution, and workflow persistence when you need to send code (functions, classes) or rich objects between processes or machines.

### 2.1. Installation

```
pip install cloudpickle

```

### 2.2. Core Functions

-   `cloudpickle.dumps(obj) → bytes`

-   `cloudpickle.dump(obj, file_obj)`

-   `cloudpickle.loads(bytes_obj) → obj`

-   `cloudpickle.load(file_obj) → obj`

### 2.3. Objects Supported

1.  **Lambdas**

2.  **Local / nested functions**

3.  **Closures** (functions capturing external variables)

4.  **Dynamically created classes**

5.  **`functools.partial`** functions

6.  **Generator functions** (but not live generator instances)

7.  **Instances** carrying methods and closures

### 2.4. Usage Examples

```
import cloudpickle
```

# 1. Serialize a lambda
```
f = lambda x: x + 1
data = cloudpickle.dumps(f)
f_loaded = cloudpickle.loads(data)
print(f_loaded(10))  # 11
```
# 2. Serialize a nested function (closure)
```
def make_multiplier(n):
    def multiplier(x):
        return x * n
    return multiplier

times5 = make_multiplier(5)
payload = cloudpickle.dumps(times5)
times5_loaded = cloudpickle.loads(payload)
print(times5_loaded(3))  # 15
```
# 3. Serialize a dynamically created class
```
type_name = 'MyClass'
MyClass = type(type_name, (), {
    '__init__': lambda self, x: setattr(self, 'x', x),
    'double':   lambda self: self.x * 2
})
cls_bytes = cloudpickle.dumps(MyClass)
LoadedClass = cloudpickle.loads(cls_bytes)
inst = LoadedClass(7)
print(inst.double())  # 14

```

* * * * *

3\. Custom Wrapper Layer: `CloudPickle_utils.py`
------------------------------------------------

This module builds on top of the CoinGecko API and `cloudpickle`, providing a streamlined interface for data ingestion, serialization, and basic analysis.

### 3.1. Data Ingestion

```
fetch_bitcoin_price_history(days=1, currency='usd')

```

-   Fetches Bitcoin price history using `/market_chart`.

-   Returns a `pandas.DataFrame` indexed by UTC `timestamp`, with a `price` column.

### 3.2. Serialization Helpers

```
serialize_object(obj, filename)
deserialize_object(filename)

```

-   Wrapper over `cloudpickle.dump` / `load` for saving and loading Python objects.

### 3.3. Time Series Analysis

```
calculate_moving_average(df, window_size)
simple_trend_analysis(df)
plot_price_data(df, title, columns_to_plot=None)

```

-   Compute SMAs, basic trend (percent change), and plotting utility.

### 3.4. Multiprocessing Support

```
task_process_data_chunk(serialized_input_tuple)

```

-   Worker function for `multiprocessing.Pool`, deserializes data & function, applies analysis, and returns serialized results.

### 3.5. Quick Example

```
from CloudPickle_utils import (
    fetch_bitcoin_price_history,
    serialize_object,
    deserialize_object,
    calculate_moving_average,
    simple_trend_analysis,
    plot_price_data
)
```
# 1. Fetch 7-day data
```
 df = fetch_bitcoin_price_history(days=7, currency='usd')
```
# 2. Compute 3-day SMA
```
 df_sma = calculate_moving_average(df, window_size=3)
```

# 3. Simple trend
```
 trend = simple_trend_analysis(df_sma)
 print(trend)
```

# 4. Persist results
```
 serialize_object(df_sma, 'sma_data.pkl')
```

# 5. Plot
```
 plot_file = plot_price_data(df_sma, title='BTC 7-day SMA')
 print(f"Plot saved to: {plot_file}")
```



* * * * *

4\. Dependencies
----------------

-   `requests`

-   `pandas`

-   `cloudpickle`

-   `matplotlib`

-   `datetime` (builtin)

-   `os` (builtin)