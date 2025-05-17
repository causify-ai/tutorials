# Project README: Bitcoin Graph Analysis with Py2Neo + Neo4j

This project builds an end-to-end pipeline to ingest, store, and analyze Bitcoin transaction and market data using CoinGecko API, Neo4j, Py2Neo, and Docker.

---

## 1. How to Navigate and Run Docker Compose

Navigate to the folder that contains the Docker setup files:

```bash
cd /tutorials/DATA605/Spring2025/projects/TutorTask245_Spring2025_Real_Time_Bitcoin_Price_Processing_using_Apache_Avro/docker_data605_style/docker_data605_style/
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

## 2. How to Launch Jupyter and Streamlit

### Jupyter Notebook

After running `docker compose up`, open your browser and go to:

```
http://localhost:8888
```

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

Then open in your browser:

```
http://localhost:8501
```

---

## 3. Order of Execution

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

---

This project uses:
- **Neo4j** to model wallets and transactions as a graph
- **Py2Neo** for database operations
- **CoinGecko API** for real-time Bitcoin data
- **Docker Compose** to manage isolated environments
- **Streamlit** to build an interactive dashboard
