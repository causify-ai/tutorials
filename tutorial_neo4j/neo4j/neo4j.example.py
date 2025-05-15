# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Neo4j Example

# +
# #!sudo /venv/bin/pip install pyvis --quiet
# #!sudo /venv/bin/pip install neo4j --quiet
# #!sudo /venv/bin/pip install py2neo --quiet
# #!sudo /venv/bin/pip install networkx --quiet
# -

# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# ## Import Packages

# +
import logging
from typing import Optional

import matplotlib.pyplot as plt
import neo4j as nj
import networkx as nx
import pandas as pd

import helpers.hdbg as hdbg
import helpers.hprint as hprint

# +
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

hprint.config_notebook()
# -

# ## Start Neo4j server

# Install Neo4j.
# #!wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
# #!echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
# #!sudo apt update
# #!sudo apt install neo4j -y
# !sudo neo4j start

# +
# URI and authentication details.
# URI = "neo4j://localhost:7687"
# USER = "neo4j"
# PASSWORD = "neo4j"
# 
# # Create a driver instance.
# driver = nj.GraphDatabase.driver(URI, auth=(USER, PASSWORD))
# driver.verify_connectivity()
# _LOG.info("Connection established.")
# 
# def change_password(tx, current_password, new_password):
#     tx.run(
#         "ALTER CURRENT USER SET PASSWORD FROM $current_password TO $new_password",
#         current_password=current_password,
#         new_password=new_password,
#     )
# 
# 
# # Change the password.
# with driver.session(database="system") as session:
#     session.write_transaction(change_password, "neo4j", "new_password")
# 
# # Reconnect with the new password.
# driver = nj.GraphDatabase.driver(URI, auth=("neo4j", "new_password"))
# driver.verify_connectivity()
# _LOG.info("Connection established.")
# -

# ## Load the dataset

# Load the dataset into a Pandas DataFrame for initial processing.
csv_file = "data/netflix.csv"
data = pd.read_csv(csv_file)
data.head()

# ## Clean the dataset

# Replace missing values and ensure data consistency.
data["cast"] = data["cast"].fillna("")
data = data.dropna(subset=["director", "country"])
data["title"] = data["title"].str.strip()
# Display the cleaned dataset.
data.head()


# ## Define a custom class

# #############################################################################
# Neo4jAPI
# #############################################################################


class Neo4jAPI:
    """
    A wrapper class for interacting with the Neo4j database.
    """

    def __init__(self, uri, user, password) -> None:
        """
        Initialize the Neo4jAPI instance.

        :param uri: URI of the Neo4j database
        :param user: username for authentication
        :param password: password for authentication
        """
        self.driver = nj.GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        """
        Close the connection to the Neo4j database.
        """
        self.driver.close()

    def run_query(self, query: str, *, parameters: Optional[dict] = None):
        """
        Run a Cypher query on the Neo4j database.

        :param query: Cypher query to run
        :param parameters: parameters to pass to the query
        :return: Neo4j Result object
        """
        with self.driver.session() as session:
            return session.run(query, parameters)

    def load_data(self, dataframe: pd.DataFrame) -> None:
        """
        Load data from a Pandas DataFrame into Neo4j.

        :param dataframe: DataFrame to load
        """
        query = """
        MERGE (movie:Movie {title: $title, release_year: $release_year})
        MERGE (director:Director {name: $director})
        MERGE (director)-[:DIRECTED]->(movie)
        """
        with self.driver.session() as session:
            for _, row in dataframe.iterrows():
                # Skip rows with missing directors or titles.
                if pd.isna(row["title"]) or pd.isna(row["director"]):
                    continue
                params = {
                    "title": row["title"],
                    "release_year": row["release_year"],
                    "director": row["director"],
                }
                session.run(query, params)

    def visualize_graph(self) -> None:
        """
        Fetch the graph data from Neo4j and visualize it with better spacing,
        smaller nodes, directed edges, and a legend.
        """
        query = """
        MATCH (d:Director)-[r:DIRECTED]->(m:Movie)
        WHERE d.name <> 'Unknown'
        RETURN d.name AS director, m.title AS movie, m.release_year AS year
        """
        with self.driver.session() as session:
            # Fetch all results into a list to prevent the consumption issue.
            results = list(session.run(query))
        # Create the directed graph.
        G = nx.DiGraph()
        for record in results:
            director = record["director"]
            movie = record["movie"]
            year = record["year"]
            # Add nodes and edges
            G.add_node(director, label="Director", type="Director")
            G.add_node(movie, label=f"{movie} ({year})", type="Movie")
            G.add_edge(director, movie, relationship="DIRECTED")
        # Layout for better spacing (adjust `k` for spacing).
        pos = nx.spring_layout(G, seed=42, k=0.5)
        # Plot the graph.
        # Larger figure for better visibility.
        plt.figure(figsize=(15, 10))
        # Draw nodes with custom sizes and colors.
        director_nodes = [
            n for n, attr in G.nodes(data=True) if attr["type"] == "Director"
        ]
        movie_nodes = [
            n for n, attr in G.nodes(data=True) if attr["type"] == "Movie"
        ]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=director_nodes,
            node_color="skyblue",
            node_size=800,
            label="Director",
        )
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=movie_nodes,
            node_color="lightgreen",
            node_size=500,
            label="Movie",
        )
        # Draw edges with arrows.
        nx.draw_networkx_edges(
            G, pos, arrowstyle="->", arrowsize=15, edge_color="gray"
        )
        # Draw labels.
        nx.draw_networkx_labels(G, pos, font_size=10, font_color="black")
        # Draw edge labels.
        edge_labels = nx.get_edge_attributes(G, "relationship")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        # Add legend.
        plt.legend(scatterpoints=1, loc="upper right", fontsize=10)
        # Title and display.
        plt.title("Movie-Director Graph", fontsize=16)
        plt.axis("off")
        plt.show()


# ## Initialize Neo4j API

# Create an instance of the Neo4jAPI class.
neo4j_api = Neo4jAPI(
    uri="neo4j://localhost:7687", user="neo4j", password="new_password"
)

# ## Load Data Into Neo4j

# Load the dataset into the Neo4j database.
neo4j_api.load_data(data[:40])

# ## Visualize the Graph

# Generate an interactive visualization of the Neo4j graph.
neo4j_api.visualize_graph()

# ## Close the Neo4j Connection

# Clean up by closing the connection to the database
neo4j_api.close()
