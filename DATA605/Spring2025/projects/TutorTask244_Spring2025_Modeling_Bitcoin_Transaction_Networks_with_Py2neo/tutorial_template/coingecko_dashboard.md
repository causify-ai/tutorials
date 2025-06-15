# coingecko_dashboard.py - Streamlit Dashboard for Bitcoin Graph Analysis

This file builds an interactive Streamlit dashboard that allows you to:
- Ingest real-time Bitcoin price and volume data from the CoinGecko API
- Store that data as a graph in a Neo4j database using Py2Neo
- Analyze wallet behaviors, transaction patterns, and market movements
- Visualize key metrics using tabs like time series charts, wallet tiers, and lookup tools

It combines real-world data with a graph-based backend to give users a dynamic interface for graph analytics.

---

## How the Dashboard Works

The dashboard is divided into four main tabs:
1. **Time Series:** Line chart showing Bitcoin price and volume over time
2. **Wallet Analytics:** Classify wallets as WHALE or NORMAL based on total sent amount
3. **Frequent Transactions:** Display sender–receiver pairs with most transactions
4. **Wallet Lookup:** Search for a specific wallet to view its tier and transaction stats

Data ingestion is triggered manually using the sidebar, which pulls price and volume snapshots from CoinGecko and stores them in Neo4j as a graph.

---

## Neo4j Graph Structure

- Each wallet is stored as a node labeled `Address`
- Each transaction is a `SENT` relationship with properties: `amount` and `timestamp`
- Bitcoin price points are stored as `PriceSnapshot` nodes linked to a `Coin` node via `HAS_SNAPSHOT`

---

## Cypher Queries Explained

### 1. Time Series Data
Used to fetch historical price and volume snapshots from the graph:
```cypher
MATCH (c:Coin)-[:HAS_SNAPSHOT]->(s:PriceSnapshot)
WHERE c.id = 'bitcoin'
RETURN s.timestamp AS time, s.price AS price, s.volume AS volume
ORDER BY time
```

### 2. Wallet Tier Classification
After computing total amounts sent by wallets in Python, the classification function adds a `tier` property to each wallet node.

Later, we fetch tier counts:
```cypher
MATCH (a:Address)
WHERE a.tier IS NOT NULL
RETURN a.tier AS tier, count(*) AS count
```

### 3. Frequent Transactions
Used to extract sender–receiver pairs with the most transactions:
```cypher
MATCH (a:Address)-[r:SENT]->(b:Address)
RETURN a.address AS sender, b.address AS receiver, count(*) AS tx_count
ORDER BY tx_count DESC
LIMIT 10
```

### 4. Wallet Lookup
Used to retrieve tier and basic transaction metadata for a user-supplied wallet address:
```cypher
MATCH (a:Address {address: 'wallet_0'})
OPTIONAL MATCH (a)-[:SENT]->(r:Address)
OPTIONAL MATCH (s:Address)-[:SENT]->(a)
RETURN a.address AS wallet, a.tier AS tier,
       count(DISTINCT r) AS sent_to,
       count(DISTINCT s) AS received_from
```

---

## Summary

This file lets you explore Bitcoin market behavior and wallet interactions using:
- Real-time API data
- Graph modeling in Neo4j
- Visualizations powered by Streamlit

It's a practical example of combining external APIs with graph databases and Python-based UI tools for real-world analysis.