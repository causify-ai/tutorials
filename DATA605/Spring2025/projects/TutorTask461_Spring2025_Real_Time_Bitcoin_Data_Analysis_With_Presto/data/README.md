Sure! Here's the complete `README.md` as a single copy-paste-friendly Markdown file:

---

```markdown
# Real-Time Bitcoin Data Analysis with Presto

This project provides a complete pipeline for fetching, storing, querying, and visualizing Bitcoin transaction data using Presto and Python.

## 📦 Project Structure

```

.
├── config.py                 # API key configuration
├── utils.py                 # Core functions for Presto queries and plotting
├── main.py                  # Script to fetch Bitcoin market data and save as Parquet
├── analysis.ipynb           # Jupyter Notebook for querying and visualizing results
└── data/                    # Parquet storage directory (Hive-compatible)

````

## 🔧 Requirements

- Python 3.8+
- Docker (for running Presto & Hive)
- Hive + Presto setup (configured to read from `/data/warehouse`)
- Python packages:
  ```bash
  pip install pandas matplotlib pyhive[presto]
````

## 🚀 Features

### 1. Fetch Historical Bitcoin Data

* Uses CoinGecko API to fetch historical BTC-USD prices from a given start date to the present.
* Saves the data as a Parquet file in a Hive-compatible location.

### 2. Query Data with Presto

* Connects to a Presto instance.
* Executes SQL queries to:

  * Calculate daily transaction volume.
  * Compute average transaction values over time.

### 3. Visualize Results

* Time series plots for:

  * Bitcoin transaction volume over time.
  * Average value of transactions per day.

## 🗃️ Data Table Example (`bitcoin_transactions`)

The Presto table should be set up with a schema like:

```sql
CREATE TABLE hive.default.bitcoin_transactions (
    timestamp timestamp,
    value_usd double,
    address varchar
)
WITH (
    format = 'PARQUET',
    external_location = 'file:///data/warehouse/bitcoin_transactions/',
    external = true
);
```

## 📈 Example Output

* Line chart of transaction counts per day
* Line chart of average transaction value per day

## 📌 Usage

1. Run `main.py` to fetch and save data.
2. Start your Presto + Hive stack (e.g. using Docker Compose).
3. Open `analysis.ipynb` to run SQL queries and generate visualizations.

## ✅ Future Improvements

* Add interactive dashboards (e.g., Plotly or Dash)
* Support for filtering by address type or transaction type

---

Built with ❤️ for Bitcoin data enthusiasts and data engineers.

```

---

Let me know if you'd like a `.md` file export or want me to include Docker configuration too.
```
