<!-- toc -->
- [CoinGecko API Tutorial](#coingecko-api-tutorial)  
  * [Table of Contents](#table-of-contents)  
    + [Hierarchy](#hierarchy)  
  * [General Guidelines](#general-guidelines)  
  * [Overview](#overview)  
  * [Class: BitcoinDataCollector](#class-bitcoindatacollector)  
    + [__init__](#__init__)  
    + [fetch_price](#fetch_price)  
    + [collect](#collect)  
    + [save_to_csv](#save_to_csv)  
  * [Execution](#execution)  
<!-- tocstop -->

# CoinGecko API Tutorial

## Table of Contents

The markdown code includes a TOC and follows proper heading structure.

### Hierarchy

Hierarchy of the markdown file:

```
# Level 1 (Used as title)
## Level 2
### Level 3
```

Level 1 Headings indicate the title as `# <tool> Tutorial` (e.g., `CoinGecko API Tutorial`)

## General Guidelines

- Follow the instructions in [README](/DATA605/DATA605_Spring2025/README.md) on what to write in the API tutorial.
- Describe how the API works based on what was explored in `template.API.py/ipynb`.
- This tutorial follows the naming convention: `coingecko.API.md`
- Additional references:
  - CoinGecko API Reference: [https://www.coingecko.com/en/api/documentation](https://www.coingecko.com/en/api/documentation)
  - Coding Style Guide: [Causify Style Guide](https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md)
  - For pipeline and ingestion, refer to: `dataprep.connector.API.md`

---

## Overview

This script fetches and stores real-time Bitcoin price data using the CoinGecko API. It:

- Uses `requests` to hit the CoinGecko `/simple/price` endpoint.
- Records prices every 10 seconds over a 3-hour period.
- Timestamps each record using `pandas`.
- Saves the data into a CSV file using `DataFrame.to_csv()`.

The script is structured using a `BitcoinDataCollector` class with clear logging, error handling, and modular design.

---

## Class: BitcoinDataCollector

Encapsulates all functionality for real-time price collection.

### `__init__`

Initializes the object with:

- `interval_seconds`: Time between API calls (default: 10).
- `duration_seconds`: Total collection time (default: 10800, i.e., 3 hours).
- `self.iterations`: Number of times the API is called.
- `self.data`: A list to store each timestamped price.

### `fetch_price`

- Sends a GET request to CoinGecko API:  
  `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd`
- On success, returns:  
  `{ 'timestamp': <current_time>, 'price_usd': <price> }`
- On failure, logs the error and returns `None`.

### `collect`

- Runs a loop for `self.iterations` times.
- Calls `fetch_price()` and appends the result to `self.data`.
- Logs the price every time it's successfully fetched.
- Waits `interval_seconds` between each API call.

### `save_to_csv`

- Converts `self.data` into a pandas DataFrame.
- Saves it to `bitcoin_real_time_data.csv`.
- Logs a confirmation once saved.

---

## Execution

The script starts with:

```python
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collector = BitcoinDataCollector()
    collector.collect()
    collector.save_to_csv()
```

- Sets up logging.
- Creates an instance of `BitcoinDataCollector`.
- Calls the `collect()` method to fetch live Bitcoin data.
- Exports the data to a CSV file after completion.
