<!-- toc -->

- [coingecko_API.ipynb - Py2Neo + API Integration Tutorial](#coingecko_apiipynb---py2neo--api-integration-tutorial)
  * [1. Purpose](#1-purpose)
  * [2. Steps in the Notebook](#2-steps-in-the-notebook)
    + [2.1 Connect to Neo4j](#21-connect-to-neo4j)
    + [2.2 Set Parameters](#22-set-parameters)
    + [2.3 Fetch and Store Data](#23-fetch-and-store-data)
  * [3. Cypher Operations Used](#3-cypher-operations-used)
  * [4. Summary](#4-summary)

<!-- tocstop -->

# coingecko_API.ipynb - Py2Neo + API Integration Tutorial

This notebook demonstrates how to use the Py2Neo library to fetch Bitcoin market data from the CoinGecko API and store it in a Neo4j graph database. It’s designed to be simple and help you learn how API data can be translated into graph structure.

---

## 1. Purpose

- Connect to a Neo4j database using Py2Neo
- Pull real Bitcoin data from CoinGecko
- Insert transactions and market snapshots into the graph

---

## 2. Steps in the Notebook

### 2.1 Connect to Neo4j

The notebook imports `connect_to_neo4j()` from `neo4j_utils.py` to create a live graph connection.

```python
graph = connect_to_neo4j()
```

---

### 2.2 Set Parameters

Two key parameters are defined:

- `DAYS`: how many days of historical data to fetch from CoinGecko
- `NUM_WALLETS`: number of wallets to simulate in transaction generation

---

### 2.3 Fetch and Store Data

The following steps are done in one flow:

```python
txs, prices, volumes = fetch_price_volume(days=DAYS, num_wallets=NUM_WALLETS)
for tx in txs:
    insert_transaction(graph, *tx)
```

- Each transaction is stored as a `:SENT` relationship between two `:Address` nodes.
- A `Coin` node is also created (if it doesn't already exist).
- Price and volume snapshots are added using `insert_price_snapshots()`.

---

## 3. Cypher Operations Used

Although Cypher isn’t written manually here, the Py2Neo functions under the hood use:

- `MERGE` to prevent duplicate nodes (wallets, coins)
- `CREATE` for relationships (`SENT`, `HAS_SNAPSHOT`)
- Implicit `MATCH`/`MERGE` during graph queries and inserts

This structure ensures a consistent graph schema with reusable entities.

---

## 4. Summary

This notebook is a compact demonstration of how to go from:
- API data (CoinGecko)
- To real relationships (Neo4j)
- Using a minimal Py2Neo-based interface

It’s a great starting point if you’re learning how to use APIs and graphs together.