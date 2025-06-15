# Project README: Modeling Bitcoin Transaction Networks with with Py2Neo

- **Author**: Rishi Koushik Sridharan  
- **Date**: 2025-05-17

This project contains the following files and folders:

---

## `docker_data605_style`

This folder contains all Docker-related files for running Jupyter and Neo4j in isolated containers:
- `Dockerfile`, `docker-compose.yml`, and various `*.sh` scripts for building, running, and managing services

---

## Project Files

- `README.md` — Main documentation for running and understanding the project

- `coingecko.API.ipynb` — Jupyter notebook for fetching Bitcoin price/volume data from CoinGecko and inserting it into Neo4j

- `coingecko.example.ipynb` — Notebook to perform analysis using Cypher queries and generate visualizations

- `coingecko_dashboard.py` — Streamlit dashboard that allows interactive exploration of Bitcoin graph data

- `coingecko.API.md` — Markdown file explaining the API ingestion notebook

- `coingecko.example.md` — Markdown file describing the analysis notebook

- `neo4j_utils.py` — Python utility functions to connect to Neo4j, ingest data, run Cypher queries, and classify wallets

- `neo4j_utils.md` — Tutorial-style documentation for learning Py2Neo with practical Cypher examples

---


This project builds an end-to-end pipeline to ingest, store, and analyze Bitcoin transaction and market data using CoinGecko API, Neo4j, Py2Neo, and Docker.

## Understanding Neo4j and Py2Neo

**Neo4j** is a graph database that stores data using nodes and relationships instead of traditional rows and tables. It’s ideal for scenarios where relationships are just as important as the data itself — such as social networks, recommendation systems, or transaction histories.

In this project:
- Each wallet is a **node** labeled `Address`
- Each Bitcoin transaction is a **relationship** labeled `SENT`
- Each market data point is stored as a `PriceSnapshot` node

This structure makes it easy to visualize who is transacting with whom, detect patterns, and run graph-based queries like "who are the top senders?" or "which wallets interact frequently?"

**Py2Neo** is a Python client library that allows you to connect to a Neo4j database and work with it directly from Python. Instead of writing raw database queries all the time, you can create, query, and manage graph data using Python objects.

Example:
```
from py2neo import Node, Relationship

a = Node("Address", address="wallet_1")
b = Node("Address", address="wallet_2")
graph.create(Relationship(a, "SENT", b, amount=1.5))
```

This project uses Py2Neo to insert data fetched from the CoinGecko API and to perform Cypher queries for analysis.

---


Here is the overall architecture of the project. The overall steps involved are: 
1) Docker environment is setup and Containers for Jupyter and Neo4J are created.
2) In Jupyter, when the coingecko.API.ipynb is run, the data is fetched from the Bitcoin API, Py2Neo is used to run Cypher queries to store the data in GraphBD.
3) Once the data is ingested, it is ready to be used in the analysis notebook and Streamlit app
4) Execute coingecko.example.ipynb to run the analysis notebook
5) Open the streamlit app in the appropriate app to vary the parameters and look at different visualizations.

   More in depth instructions are available below.

![Analysis](https://github.com/user-attachments/assets/1392461d-d311-48e0-9ba8-d7ba387916df)


---

## Step 1. How to Navigate and Run Docker Compose

Navigate to the folder that contains the Docker setup files:

```bash
cd /tutorials/DATA605/Spring2025/projects/TutorTask244_Spring2025_Modeling_Bitcoin_Transaction_Networks_with_Py2neo/tutorial_template/docker_data605_style/
```

Then build and run the containers:

```bash
docker compose build --no-cache
docker compose up
```

This will launch two services:
- A Jupyter Notebook server (default port 8888)
- A Neo4j database (default ports 7474, 7687)

---

## Step 2. How to Launch Jupyter and Streamlit

### Jupyter Notebook

After running `docker compose up`, open your browser and go to:

```
http://localhost:8888
```

If the above link does not work, check the terminal for a port that starts with 127.0.1.1 and use that link in the browser.

You can now open:
- `coingecko_API.ipynb` for data ingestion
- `coingecko_example.ipynb` for analysis

---


### Streamlit Dashboard

After running `docker compose up`, run the following script in a separate terminal:
```
docker exec -it jupyter_data605 bash
streamlit run coingecko_dashboard.py
```

Then, open your browser and go to:
```
http://localhost:8501
```

---


## Order of Execution- Summary

Follow these steps to run the project in order:

1. Start Docker:  
   `cd docker_data605_style && docker compose up`

2. Open `http://localhost:8888` and run **`coingecko_API.ipynb`**  
   This fetches data from CoinGecko and stores it in Neo4j

3. Run **`coingecko_example.ipynb`**  
   This performs Cypher-based analysis and generates plots

4. (Optional) Launch the dashboard:  
   `docker exec -it jupyter_data605 bash`  
   `streamlit run coingecko_dashboard.py`
   Launch the streamlit app at `http://localhost:8501`

---

This project uses:
- **Neo4j** to model wallets and transactions as a graph
- **Py2Neo** for database operations
- **CoinGecko API** for real-time Bitcoin data
- **Docker Compose** to manage isolated environments
- **Streamlit** to build an interactive dashboard
