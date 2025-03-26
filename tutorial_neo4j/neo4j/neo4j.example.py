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

# !sudo /venv/bin/pip install pyvis --quiet

# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# ## Import Packages

# +
import datetime
import logging

import neo4j as nj
import py2neo as pyneo
import pyvis.network as ntwk
import pandas as pd 
import networkx as nx
import matplotlib.pyplot as plt
import IPython.display as ipd
# -

# ## Load the dataset

# +
# ## Step 1: Load the dataset.
# Load the dataset into a Pandas DataFrame for initial processing.
csv_file = "netflix.csv"
data = pd.read_csv(csv_file)

# Let's see the how the dataset looks.
data.head()
# -

# ## Clean the dataset

# ## Step 1.1: Clean the dataset
# Replace missing values and ensure data consistency
data['cast'] = data['cast'].fillna('') 
data = data.dropna(subset=['director', 'country'])
data['title'] = data['title'].str.strip()  
# Display the cleaned dataset
data.head()


# ## Define a custom class

class Neo4jAPI:
    """
    A wrapper class for interacting with the Neo4j database.
    """
    def __init__(self, uri, user, password):
        """
        Initialize the Neo4jAPI instance.

        Args:
            uri (str): The URI of the Neo4j database.
            user (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.driver = nj.GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Close the connection to the Neo4j database.
        """
        self.driver.close()

    def run_query(self, query, parameters=None):
        """
        Run a Cypher query on the Neo4j database.

        Args:
            query (str): The Cypher query to execute.
            parameters (dict, optional): Parameters to include in the query.

        Returns:
            neo4j.Result: The result of the query execution.
        """
        with self.driver.session() as session:
            return session.run(query, parameters)

    def load_data(self, dataframe):
        """
        Load data from a Pandas DataFrame into Neo4j.
        """
        query = """
        MERGE (movie:Movie {title: $title, release_year: $release_year})
        MERGE (director:Director {name: $director})
        MERGE (director)-[:DIRECTED]->(movie)
        """
        with self.driver.session() as session:
            for _, row in dataframe.iterrows():
                # Skip rows with missing directors or titles
                if pd.isna(row['title']) or pd.isna(row['director']):
                    continue
                
                params = {
                    "title": row['title'],
                    "release_year": row['release_year'],
                    "director": row['director']
                }
                session.run(query, params)

    def visualize_graph(self):
        """
        Fetch the graph data from Neo4j and visualize it with better spacing, smaller nodes, directed edges, and a legend.
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
        director_nodes = [n for n, attr in G.nodes(data=True) if attr['type'] == "Director"]
        movie_nodes = [n for n, attr in G.nodes(data=True) if attr['type'] == "Movie"]
        nx.draw_networkx_nodes(G, pos, nodelist=director_nodes, node_color="skyblue", node_size=800, label="Director")
        nx.draw_networkx_nodes(G, pos, nodelist=movie_nodes, node_color="lightgreen", node_size=500, label="Movie")
        # Draw edges with arrows.
        nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=15, edge_color="gray")
        # Draw labels.
        nx.draw_networkx_labels(G, pos, font_size=10, font_color="black")
        # Draw edge labels.
        edge_labels = nx.get_edge_attributes(G, 'relationship')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        # Add legend.
        plt.legend(scatterpoints=1, loc="upper right", fontsize=10)
        # Title and display.
        plt.title("Movie-Director Graph", fontsize=16)
        plt.axis("off") 
        plt.show()


# ## Initialize Neo4j API

# Create an instance of the Neo4jAPI class.
neo4j_api = Neo4jAPI(uri="neo4j://localhost:7687", user="neo4j", password="new_password")

# ## Load Data Into Neo4j

# Load the dataset into the Neo4j database.
neo4j_api.load_data(data[:40])

# ## Visualize the Graph

# Generate an interactive visualization of the Neo4j graph.
neo4j_api.visualize_graph()

# ## Close the Neo4j Connection

# Clean up by closing the connection to the database
neo4j_api.close()
