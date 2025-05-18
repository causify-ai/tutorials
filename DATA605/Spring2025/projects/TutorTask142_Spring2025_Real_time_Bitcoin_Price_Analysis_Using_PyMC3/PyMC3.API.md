
# Bitcoin Price Logging System

A modular Python-based system that logs real-time Bitcoin prices using the CoinGecko API.  
The system is cleanly separated into utility functions and a driver script for extensibility and clarity.

---

## Table of Contents

- [Overview](#overview)
- [File Structure](#file-structure)
- [Getting Started](#getting-started)
- [API Usage](#api-usage)
  - [get_bitcoin_price](#get_bitcoin_price)
  - [save_to_csv](#save_to_csv)
- [Execution](#execution)
- [References](#references)

---

## Overview

This project fetches real-time Bitcoin price data using the CoinGecko API and saves it to a CSV file.  
It is modularized for clean implementation and better reusability using a separate `utils.py` file.

---

## File Structure

```
.
├── bitcoin_data_logger.py    # Main script that runs the logging loop
├── utils.py                  # Contains reusable utility functions
├── bitcoin_price_data.csv    # Output CSV file (created after running)
```

---

## Getting Started

1. Clone the repository or download the files.
2. Install dependencies using pip:
   ```bash
   pip install requests pandas
   ```
3. Run the logger script:
   ```bash
   python bitcoin_data_logger.py
   ```

---

## API Usage

### get_bitcoin_price

**Location**: `utils.py`

**Purpose**: Fetch current Bitcoin price from CoinGecko.

**Returns**:  
Tuple — (`timestamp: str`, `price: float`) or (`None, None`) on failure.

### save_to_csv

**Location**: `utils.py`

**Purpose**: Saves a row with timestamp and price to the specified CSV file.

**Params**:
- `timestamp (str)`
- `price (float)`
- `csv_file (str)`

---

## Execution

When you run `bitcoin_data_logger.py`, it:

1. Initializes the logger
2. Repeats for a configured number of entries:
   - Fetches price data using `get_bitcoin_price()`
   - Logs to CSV using `save_to_csv()`
   - Waits for a fixed interval

Modify these configurations at the top of `bitcoin_data_logger.py`:
```python
NUM_ENTRIES = 20
INTERVAL = 10
CSV_FILE = "bitcoin_price_data.csv"
```

---

## References

- [CoinGecko API](https://www.coingecko.com/en/api/documentation)
- [pandas Docs](https://pandas.pydata.org/)
- [requests Docs](https://requests.readthedocs.io/en/latest/)
- [Logging Module](https://docs.python.org/3/library/logging.html)
