<!-- toc -->

- [Snowflake API Tutorial](#Snowflake-api-tutorial)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [General Guidelines](#general-guidelines)

<!-- tocstop -->

# Snowflake API Tutorial

- Native API for `snowflake_utils.py`, a custom Python module that interfaces with Snowflake and CoinGecko APIs.

## Table of Contents

This document explains the native API layer developed for the Bitcoin price analysis project:
- Key functions in `bitcoin_utils.py`
- How to fetch and ingest data
- Query and visualize data
- Usage via `bitcoin.API.ipynb` notebook

---

### Hierarchy

```
# Level 1 (Used as title)
All the subheadings should follow the below structure:
## Level 2
### Level 3
```

Level 1 Heading is the title: `# Snowflake API Tutorial`

---

## General Guidelines

- This follows the DATA605 Spring 2025 project submission structure.
- The API functions are documented and demonstrated in `Snowflake.API.ipynb`.
- You should **not copy-paste** outputs into markdown. Instead, clearly describe the logic and steps.
- Each function is modular and designed for reuse in other scripts or dashboards.

---

### Key Functions in `snowflake_utils.py`

| Function Name                      | Purpose                                             |
|-----------------------------------|-----------------------------------------------------|
| `connect_to_snowflake()`          | Connects securely to Snowflake using `.env` file    |
| `fetch_bitcoin_price()`           | Pulls current BTC price from CoinGecko API          |
| `insert_price_to_snowflake()`     | Inserts a single BTC record into Snowflake          |
| `load_historical_prices_to_snowflake()` | Loads 90-day historical BTC data              |
| `query_all_prices()`              | Retrieves all BTC price data as a pandas DataFrame  |

---

### API Usage

The API is imported in `Snowflake.API.ipynb` and called as follows:

```python
from bitcoin_utils import (
    connect_to_snowflake,
    fetch_bitcoin_price,
    insert_price_to_snowflake,
    query_all_prices,
    load_historical_prices_to_snowflake
)
```

The notebook demonstrates:
- Connecting to Snowflake
- Fetching current and historical BTC prices
- Inserting records
- Querying the full table
- Plotting trends using pandas + matplotlib

---

