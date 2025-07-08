<!-- toc -->

- [PyArrow Tutorial](#pyarrow-tutorial)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [General Guidelines](#general-guidelines)
  * [Introduction](#introduction)
  * [Key Concepts](#key-concepts)
  * [Use Case: Real-Time Bitcoin Price Streaming](#use-case-real-time-bitcoin-price-streaming)
    + [Step 1: Fetch Live Data](#step-1-fetch-live-data)
    + [Step 2: Store in PyArrow Table](#step-2-store-in-pyarrow-table)
    + [Step 3: Write as Parquet](#step-3-write-as-parquet)
    + [Step 4: Read from Parquet](#step-4-read-from-parquet)
  * [References](#references)

[PyArrow](https://arrow.apache.org/docs/python/) is the Python implementation of Apache Arrow, a cross-language development platform for in-memory data. It is designed for efficient analytics, particularly in big data and streaming scenarios.

In this tutorial, we demonstrate how to use PyArrow to collect, structure, and persist real-time Bitcoin price data using the CoinGecko API.

## Key Concepts

- **Arrow Tables**: Columnar memory layout for fast analytics.
- **Parquet**: Compressed columnar storage format for efficient file-based persistence.
- **Streaming**: PyArrow supports batched memory ingestion for live or time-series data.

## Use Case: Real-Time Bitcoin Price Streaming

In this use case, we use PyArrow to store and manipulate streamed price data efficiently.

### Step 1: Fetch Live Data

Use `fetch_current_bitcoin_price(api_key)` to get the current Bitcoin price:

```python
timestamp, price = fetch_current_bitcoin_price(api_key)

This returns the current UTC timestamp and Bitcoin price in USD.

#### Step 2: Store in PyArrow Table
We batch multiple price points using PyArrow's schema and conversion methods:

schema = pa.schema([
    ('timestamp', pa.string()),
    ('price_usd', pa.float64())
])

table = pa.Table.from_pylist(batch_data, schema=schema)
batch_data is a list of tuples: [(timestamp, price), ...].

#### Step 3: Write as Parquet
You can write the table to a Parquet file for persistent storage:

import pyarrow.parquet as pq

pq.write_table(table, "datalake/bitcoin_prices.parquet")
Ensure the target directory exists before writing.

#### Step 4: Read from Parquet
To read the data back:

loaded_table = pq.read_table("datalake/bitcoin_prices.parquet")
df = loaded_table.to_pandas()
Now, df is a Pandas DataFrame containing your saved price data.

References
PyArrow Documentation: https://arrow.apache.org/docs/python/

CoinGecko API Docs: https://www.coingecko.com/en/api/documentation
