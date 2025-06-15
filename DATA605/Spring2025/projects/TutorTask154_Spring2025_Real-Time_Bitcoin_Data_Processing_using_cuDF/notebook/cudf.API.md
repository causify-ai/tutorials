# cuDF API Documentation

This document provides a comprehensive overview of the RAPIDS cuDF API as used in the Bitcoin Data Processing project.

## Introduction to cuDF

RAPIDS cuDF is a GPU DataFrame library for loading, joining, aggregating, filtering, and otherwise manipulating data. cuDF provides a pandas-like API that will be familiar to data scientists, so they can use it to easily accelerate their workflows without going into the details of CUDA programming.

## Key Differences from pandas

While cuDF aims to provide a pandas-like API, there are some important differences:

1. **GPU Acceleration**: cuDF operations run on the GPU, offering significant performance benefits for large datasets.
2. **Memory Management**: cuDF manages GPU memory differently than pandas manages CPU memory.
3. **Data Types**: Some pandas data types are not available in cuDF or behave differently.
4. **Method Support**: Not all pandas methods are available in cuDF, and some behave differently.
5. **Performance Characteristics**: Some operations that are slow in pandas may be fast in cuDF and vice versa.

## Core cuDF Data Structures

### DataFrame

The primary data structure in cuDF is the DataFrame, similar to pandas:

```python
import cudf

# Create a DataFrame from a dictionary
df = cudf.DataFrame({
    'A': [1, 2, 3, 4, 5],
    'B': ['a', 'b', 'c', 'd', 'e']
})

# Create a DataFrame from a pandas DataFrame
import pandas as pd
pandas_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
cudf_df = cudf.DataFrame.from_pandas(pandas_df)
```

### Series

A Series is a single column of data:

```python
# Create a Series directly
s = cudf.Series([1, 2, 3, 4, 5])

# Access a Series from a DataFrame
s = df['A']
```

## Data Loading and Output

cuDF provides functions to read data from and write data to various file formats:

```python
# Read from CSV
df = cudf.read_csv('data.csv')

# Read from Parquet
df = cudf.read_parquet('data.parquet')

# Write to CSV
df.to_csv('output.csv', index=False)

# Write to Parquet
df.to_parquet('output.parquet')

# Convert to pandas
pandas_df = df.to_pandas()
```

## Data Manipulation

### Indexing and Selection

```python
# Select a single column
s = df['A']

# Select multiple columns
df_subset = df[['A', 'B']]

# Select rows by position
df_rows = df.iloc[0:5]

# Select rows by label
df_rows = df.loc[df.index[0:5]]

# Boolean indexing
df_filtered = df[df['A'] > 3]
```

### Data Cleaning

```python
# Handle missing values
df = df.fillna(0)  # Fill with a value
df = df.dropna()   # Drop rows with missing values

# Drop duplicates
df = df.drop_duplicates()
```

### Data Transformation

```python
# Apply a function to a column
df['A_squared'] = df['A'] ** 2

# Apply a function to each element
df['A_sqrt'] = df['A'].map(lambda x: x ** 0.5)
```

## Aggregation and Grouping

```python
# Basic aggregation
mean_value = df['A'].mean()
sum_value = df['A'].sum()
min_value = df['A'].min()
max_value = df['A'].max()

# GroupBy operations
grouped = df.groupby('B')
group_means = grouped.mean()
```

## Time Series Functionality

cuDF provides functionality for working with time series data, which is heavily used in the Bitcoin Data Processing project:

```python
# Convert string to datetime
df['timestamp'] = cudf.to_datetime(df['timestamp_str'])

# Set timestamp as index
df = df.set_index('timestamp')

# Resample time series data
daily_data = df.resample('D').mean()

# Rolling statistics
df['rolling_mean'] = df['value'].rolling(window=7).mean()
df['rolling_std'] = df['value'].rolling(window=7).std()
```

## Performance Tips

To get the best performance from cuDF:

1. **Batch Operations**: Perform operations in batches rather than row-by-row
2. **Minimize Host-Device Transfers**: Avoid frequent conversions between pandas and cuDF
3. **Use Efficient File Formats**: Parquet is generally faster than CSV
4. **Leverage GPU-Specific Optimizations**: Use cuDF's GPU-optimized algorithms where possible
5. **Monitor Memory Usage**: Large datasets can exhaust GPU memory

## Example: Technical Indicator Calculation

Below is an example showing how to calculate a Simple Moving Average (SMA) using cuDF:

```python
import cudf
import numpy as np

# Load data
df = cudf.read_csv('bitcoin_prices.csv')
df['timestamp'] = cudf.to_datetime(df['timestamp'])

# Calculate 7-day SMA
df['sma_7'] = df['price'].rolling(window=7).mean()

# Calculate 14-day RSI
delta = df['price'].diff()
gain = delta.copy()
loss = delta.copy()
gain = gain.where(gain > 0, 0)
loss = loss.where(loss < 0, 0).abs()
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
df['rsi_14'] = 100 - (100 / (1 + rs))
```

## Resources

- Official RAPIDS cuDF Documentation: https://docs.rapids.ai/api/cudf/stable/
- RAPIDS GitHub Repository: https://github.com/rapidsai/cudf
- NVIDIA RAPIDS Getting Started: https://developer.nvidia.com/rapids 