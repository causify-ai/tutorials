<!-- toc -->

- [coingecko_example.ipynb - Bitcoin Graph Analysis Tutorial](#coingecko_exampleipynb---bitcoin-graph-analysis-tutorial)
  * [1. Overview](#1-overview)
  * [2. Visualizations and Queries](#2-visualizations-and-queries)
    + [2.1 Top Senders](#21-top-senders)
    + [2.2 Frequent Pairs](#22-frequent-pairs)
    + [2.3 Mutual Transaction Network](#23-mutual-transaction-network)
    + [2.4 Wallet Tier Classification](#24-wallet-tier-classification)
    + [2.5 Bitcoin Price Trend](#25-bitcoin-price-trend)
  * [3. Tools Used](#3-tools-used)
  * [4. Summary](#4-summary)

<!-- tocstop -->

# coingecko_example.ipynb - Bitcoin Graph Analysis Tutorial

This notebook focuses on analyzing data stored in a Neo4j graph database using Py2Neo. It builds on the ingestion from `coingecko_API.ipynb` and explores transaction behavior, wallet classifications, and market trends using visualizations.

---

## 1. Overview

After connecting to the graph database, the notebook runs Cypher queries to get:
- Top active wallets
- Frequent sender-receiver pairs
- Bidirectional transactions
- Wallet tier classification (e.g., WHALE vs NORMAL)
- Bitcoin price movement over time

Each result is plotted to reveal structure in the data.

---

## 2. Visualizations and Queries

### 2.1 Top Senders

The notebook queries the number of outgoing transactions per wallet:

```cypher
MATCH (a:Address)-[:SENT]->()
RETURN a.address AS sender, count(*) AS tx_count
ORDER BY tx_count DESC
LIMIT 5
```

This is shown using a vertical bar chart.

---

### 2.2 Frequent Pairs

Sender-receiver pairs are identified based on how many transactions occurred between them:

```cypher
MATCH (a:Address)-[r:SENT]->(b:Address)
RETURN a.address AS sender, b.address AS receiver, count(*) AS tx_count
ORDER BY tx_count DESC
LIMIT 10
```

These are shown in a horizontal bar chart with labels like `wallet_X → wallet_Y`.

---

### 2.3 Mutual Transaction Network

This graph shows pairs that sent transactions to each other:

```cypher
MATCH (a:Address)-[:SENT]->(b:Address)
MATCH (b)-[:SENT]->(a)
RETURN DISTINCT a.address AS one, b.address AS two
```

A `networkx` graph is plotted using `nx.draw()` to show bidirectional relationships.

---

### 2.4 Wallet Tier Classification

Wallets are classified into WHALE or NORMAL using:

```cypher
MATCH (a:Address)
RETURN a.tier AS tier, count(*) AS count
```

Bar chart shows distribution of wallets by tier.

---

### 2.5 Bitcoin Price Trend

The price history stored from CoinGecko is queried and visualized:

```cypher
MATCH (c:Coin)-[:HAS_SNAPSHOT]->(s:PriceSnapshot)
WHERE c.id = 'bitcoin'
RETURN s.timestamp AS time, s.price AS price
ORDER BY time
```

Plotted as a time series to show how price changed over time.

---

## 3. Tools Used

- Matplotlib for all plots
- NetworkX for graph visualization
- Pandas for data manipulation
- Py2Neo to connect and run Cypher queries

---

## 4. Summary

This notebook is a practical demo of Cypher + Python graph analysis. It provides a good reference for analyzing transaction graphs using real blockchain-inspired data with Neo4j and Py2Neo.