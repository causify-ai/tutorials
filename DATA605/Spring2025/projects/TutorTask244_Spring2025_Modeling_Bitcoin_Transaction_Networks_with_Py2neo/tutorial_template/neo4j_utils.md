<!-- toc -->

- [neo4j_utils.py - Py2Neo Tutorial](#neo4j_utils.py---py2neo-tutorial)
  * [1. Connecting to Neo4j](#1-connecting-to-neo4j)
  * [2. Inserting Transactions](#2-inserting-transactions)
  * [3. Fetching Bitcoin Data](#3-fetching-bitcoin-data)
  * [4. Adding Price Snapshots](#4-adding-price-snapshots)
  * [5. Cypher Queries for Analysis](#5-cypher-queries-for-analysis)
    + [Top Senders](#top-senders)
    + [Frequent Pairs](#frequent-pairs)
    + [Mutual Transactions](#mutual-transactions)
  * [6. Classifying Wallets](#6-classifying-wallets)
  * [Summary](#summary)

<!-- tocstop -->

# neo4j_utils.py - Py2Neo Tutorial

This file contains utility functions to help you connect to a Neo4j graph database and work with data using the Py2Neo library. It’s designed to help you learn the basics of using Neo4j with Python in under an hour — including how to connect, insert data, run Cypher queries, and do simple graph analysis.

---

## 1. Connecting to Neo4j

We use `py2neo.Graph` to connect to the Neo4j database. The credentials and URI are pulled from environment variables so that they don’t have to be hard-coded.

```python
from py2neo import Graph
import os

def connect_to_neo4j():
    return Graph(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS")))
```

Once connected, you can run Cypher queries using `graph.run(...)`.

---

## 2. Inserting Transactions

To simulate wallet-to-wallet Bitcoin transfers, we define this function:

```python
def insert_transaction(graph, sender, receiver, amount, timestamp):
    ...
```

It creates `Address` nodes for sender and receiver, and a `SENT` relationship between them with amount and timestamp. We use `MERGE` to avoid duplicate nodes.

---

## 3. Fetching Bitcoin Data

We use CoinGecko’s free API to get historical price and volume data. Based on that, we simulate transactions between a number of randomly selected wallets:

```python
def fetch_price_volume(days=1, num_wallets=20):
    ...
```

This returns a list of transactions (sender, receiver, amount, timestamp) and the raw price/volume data.

---

## 4. Adding Price Snapshots

To store price and volume history in the graph, we create snapshot nodes:

```python
def insert_price_snapshots(graph, coin_id, prices, volumes):
    ...
```

Each snapshot gets linked to a `Coin` node using the `HAS_SNAPSHOT` relationship.

---

## 5. Cypher Queries for Analysis

We define some reusable queries to analyze the graph data.

### Top Senders

Returns addresses with the most outgoing transactions:

```cypher
MATCH (a:Address)-[:SENT]->()
RETURN a.address AS sender, count(*) AS tx_count
ORDER BY tx_count DESC
LIMIT 5
```

### Frequent Pairs

Returns sender-receiver pairs with the highest transaction count:

```cypher
MATCH (a:Address)-[r:SENT]->(b:Address)
RETURN a.address AS sender, b.address AS receiver, count(*) AS tx_count
ORDER BY tx_count DESC
LIMIT 10
```

### Mutual Transactions

Returns address pairs that sent transactions to each other:

```cypher
MATCH (a:Address)-[:SENT]->(b:Address)
MATCH (b)-[:SENT]->(a)
RETURN DISTINCT a.address AS one, b.address AS two
```

---

## 6. Classifying Wallets

We assign each wallet a "tier" — either WHALE or NORMAL — based on how much Bitcoin it has sent compared to others.

```python
def classify_wallet_tiers(graph, whale_percentile=10):
    ...
```

The top X% of wallets by total sent amount are marked as WHALEs. The rest are NORMAL.

---

## Summary

This file forms the backend logic for both the Jupyter notebook and the Streamlit dashboard. It helps:
- Connect to the graph
- Ingest Bitcoin transaction and price data
- Run Cypher queries
- Classify wallets

If you’re new to Py2Neo, this file is a great starting point to understand how to combine real-world APIs with a graph database.