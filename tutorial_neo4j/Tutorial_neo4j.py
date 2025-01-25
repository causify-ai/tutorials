# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Introduction to Neo4j
#
# What is `Neo4j`?
# `Neo4j` is a graph database management system developed by Neo4j, Inc. It is an ACID-compliant transactional database with native graph storage and processing. In this tutorial, we will learn how to use Neo4j with Python using the `neo4j` library.
#
#
# ## Learning Objectives
# - Understand the basics of Neo4j and graph databases.
# - Learn how to set up and connect to Neo4j.
# - Create, query, and manipulate data in Neo4j using Cypher.
# - Explore visualization techniques for graph data.
#
# ## Prerequisites
# - Neo4j installed and running on your system.
# - Python installed with `neo4j` and `py2neo` libraries.
#     * `neo4j` is library that serves as a python client to establish connection to
#        Neo4j database servers.
#     * `py2neo`
# - This is done through building the docker image. Refer `xyz.md`
#
#

# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# # Import libraries

# +
import datetime
import logging

import neo4j as nj
import py2neo as pyneo
import networkx as nx
import matplotlib.pyplot as plt

import helpers.hdbg as hdbg
import helpers.hpandas as hpandas
import helpers.hprint as hprint

# +
# Setup notebook.
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

hprint.config_notebook()
# -

# # Setting up Neo4j
#
# Default Ports
# Neo4j uses the following default ports:
# - `7474`: `HTTP` port for Neo4j Browser and REST API.
# - `7687`: `Bolt` protocol port for database queries.
# - `7473`: `HTTPS` port for Neo4j Browser (optional, if HTTPS is enabled).
#
# These default ports cannot be changed dynamically. If we need to change, we have to do it through neo4j.conf

# ## Start Neo4j Server
#
# As discussed earlier, the default port for the `HTTP`, i.e, the database server is assigned to 7474

# !sudo neo4j start

# ## Connect to Neo4j Server
#
# Now, we have attempt to connect to the database server and query on it. For this, by default, the port that is exposed for such operations is 7687. Therefore, we have to connect to this port for all the query related operations.

# +
# URI and authentication details.
URI = "neo4j://localhost:7687"
#USER = "neo4j"
#PASSWORD = "neo4j"

# # Create a driver instance.
# driver = nj.GraphDatabase.driver(URI, auth=(USER, PASSWORD))
# driver.verify_connectivity()
# print("Connection established.")
# -

# ## Update Password of Neo4j database
#
# This is a mandatory step. The default credentials will be accepted as authentication while pushing changes to the database. Remeber that once changed, the updates are permanent and will only be reset in a clean reinstallation.

# +
# The first step once you have created a session is to change the password. You can do this using the following command:
def change_password(tx, current_password, new_password):
    tx.run("ALTER CURRENT USER SET PASSWORD FROM $current_password TO $new_password",
           current_password=current_password, new_password=new_password)
    
# Change the password.
with driver.session(database="system") as session:
    session.write_transaction(change_password, "neo4j", "new_password")

# Reconnect with the new password.
driver = nj.GraphDatabase.driver(URI, auth=("neo4j", "new_password"))
driver.verify_connectivity()
print("Connection established.")
# -

# # Check the Neo4j graph

# +
# Connect to the graph database.
graph = Graph(URI, auth=(USER, "new_password"))


def view_graph(graph):
    nodes = graph.nodes.match()
    relationships = graph.relationships.match()
    print("Nodes in the graph:")
    for node in nodes:
        print(node)
    print("\nRelationships in the graph:")
    for relationship in relationships:
        print(relationship)


# -

# # Basic Concepts
#
# In Neo4j, data is stored as nodes, relationships, and properties.
#
# - **Nodes**: Entities such as people, products, or places.
# - **Relationships**: Connections between nodes, such as "KNOWS" or "LIKES".
# - **Properties**: Key-value pairs that store information about nodes and relationships.

# ## Creating Nodes

# +
def create_person(tx, name):
    # The CREATE statement is used to create a new node in the database.
    # In this example, we create a node with the label 'Person' and a property 'name'.
    tx.run("CREATE (a:Person {name: $name})", name=name)

def create_node_with_label(tx, label, name):
    # Create a node with a specified label and a property 'name'.
    # The label is provided as a parameter.
    tx.run(f"CREATE (a:{label} {{name: $name}})", name=name)

def create_node_with_multiple_labels(tx, labels, name):
    # Create a node with multiple labels and a property 'name'.
    # The labels are provided as a list and joined with ':'.
    label_str = ":".join(labels)
    tx.run(f"CREATE (a:{label_str} {{name: $name}})", name=name)

def create_node_with_properties(tx, label, properties):
    # Create a node with a specified label and multiple properties.
    # The properties are provided as a dictionary.
    props_str = ", ".join([f"{key}: ${key}" for key in properties.keys()])
    tx.run(f"CREATE (a:{label} {{{props_str}}})", **properties)

def return_created_node(tx, label, name):
    # Create a node with a specified label and a property 'name', then return the created node.
    result = tx.run(f"CREATE (a:{label} {{name: $name}}) RETURN a", name=name)
    return result.single()[0]

# Use the session to write the transactions
with driver.session() as session:
    # Create a node with the label 'Person' and the name 'Dave'
    session.execute_write(create_person, "Dave")
    # Create a node with the label 'Employee' and the name 'Grace'
    session.execute_write(create_node_with_label, "Employee", "Grace")
    # Create a node with the labels 'Person' and 'Employee' and the name 'Hank'
    session.execute_write(create_node_with_multiple_labels, ["Person", "Employee"], "Hank")
    # Create a node with the label 'Person' and properties 'name', 'age', and 'city'
    session.execute_write(create_node_with_properties, "Person", {"name": "Ivy", "age": 28, "city": "New York"})
    # Create a node with the label 'Person' and the name 'Jack', then return the created node
    created_node = session.execute_write(return_created_node, "Person", "Jack")

print("Nodes created and returned node:", created_node)

view_graph(graph)


# -

# ## Clearing the database

# +
def clear_database(tx):
    tx.run("MATCH (n) DETACH DELETE n")
    
with driver.session() as session:
    # Clear the database
    session.execute_write(clear_database)


# -

# # Create Relations between Nodes

# +
def create_relationship(tx, node1_label, node1_name, relationship_type, node2_label, node2_name):
    # Create a relationship between two existing nodes
    tx.run(f"MATCH (a:{node1_label} {{name: $node1_name}}), (b:{node2_label} {{name: $node2_name}}) "
           f"CREATE (a)-[:{relationship_type}]->(b)",
           node1_name=node1_name, node2_name=node2_name)

def create_relationship_with_properties(tx, node1_label, node1_name, relationship_type, properties, node2_label, node2_name):
    # Create a relationship with label and properties between two existing nodes
    props_str = ", ".join([f"{key}: ${key}" for key in properties.keys()])
    tx.run(f"MATCH (a:{node1_label} {{name: $node1_name}}), (b:{node2_label} {{name: $node2_name}}) "
           f"CREATE (a)-[:{relationship_type} {{{props_str}}}]->(b)",
           node1_name=node1_name, node2_name=node2_name, **properties)

# Use the session to write the transactions
with driver.session() as session:
    # Create a relationship 'KNOWS' between 'Alice' and 'Bob'
    session.execute_write(create_relationship, "Person", "Jack", "KNOWS", "Person", "Dave")
    # Create a relationship 'WORKS_WITH' with properties between 'Grace' and 'Hank'
    session.execute_write(create_relationship_with_properties, "Employee", "Grace", "WORKS_WITH", {"since": 2020}, "Employee", "Hank")

print("Relationships created.")
view_graph(graph)


# -

# ## Write Clauses

# +
def merge_node(tx, label, properties):
    # MERGE clause is used to create a node if it does not exist, or match it if it does.
    props_str = ", ".join([f"{key}: ${key}" for key in properties.keys()])
    tx.run(f"MERGE (a:{label} {{{props_str}}})", **properties)

def merge_relationship(tx, node1_label, node1_name, relationship_type, node2_label, node2_name):
    # MERGE clause is used to create a relationship if it does not exist, or match it if it does.
    tx.run(f"MATCH (a:{node1_label} {{name: $node1_name}}), (b:{node2_label} {{name: $node2_name}}) "
           f"MERGE (a)-[:{relationship_type}]->(b)",
           node1_name=node1_name, node2_name=node2_name)

def set_properties(tx, label, name, properties):
    # SET clause is used to update properties of a node.
    props_str = ", ".join([f"a.{key} = ${key}" for key in properties.keys()])
    tx.run(f"MATCH (a:{label} {{name: $name}}) SET {props_str}", name=name, **properties)

def delete_node(tx, label, name):
    # DELETE clause is used to delete a node.
    tx.run(f"MATCH (a:{label} {{name: $name}}) DELETE a", name=name)

def delete_relationship(tx, node1_label, node1_name, relationship_type, node2_label, node2_name):
    # DELETE clause is used to delete a relationship between two nodes.
    tx.run(f"MATCH (a:{node1_label} {{name: $node1_name}})-[r:{relationship_type}]->(b:{node2_label} {{name: $node2_name}}) DELETE r",
           node1_name=node1_name, node2_name=node2_name)

# Use the session to write the transactions
with driver.session() as session:
    # Create a node with the label 'Person' and properties 'name' and 'age'
    session.execute_write(create_node_with_properties, "Person", {"name": "Alice", "age": 30})
    # Create a node with the label 'Person' and properties 'name' and 'age'
    session.execute_write(create_node_with_properties, "Person", {"name": "Bob", "age": 25})
    # Create a relationship 'KNOWS' between 'Alice' and 'Bob'
    session.execute_write(create_relationship, "Person", "Alice", "KNOWS", "Person", "Bob")
    # Merge a node with the label 'Person' and properties 'name' and 'age'
    session.execute_write(merge_node, "Person", {"name": "Charlie", "age": 25})
    # Merge a relationship 'KNOWS' between 'Alice' and 'Charlie'
    session.execute_write(merge_relationship, "Person", "Alice", "KNOWS", "Person", "Charlie")
    # Set properties 'age' and 'city' for the node 'Alice'
    session.execute_write(set_properties, "Person", "Alice", {"age": 31, "city": "New York"})
    print("\n Graph Before Deletion:")
    view_graph(graph)

    # Delete the relationship 'KNOWS' between 'Alice' and 'Bob'
    session.execute_write(delete_relationship, "Person", "Alice", "KNOWS", "Person", "Bob")
    # Delete the node 'Charlie'
    session.execute_write(delete_node, "Person", "Bob")
    print("\n Graph After Deletion:")
    view_graph(graph)


# -

# ## Read Clauses

# +
def find_all_nodes(tx):
    # Use MATCH to find all nodes.
    result = tx.run("MATCH (n) RETURN n")
    for record in result:
        print(record[0])

def find_relations(tx, name):
    # Use MATCH to find the person and who they work with.
    result = tx.run("MATCH (a:Employee {name: $name})-[:WORKS_WITH]->(Employee) "
                    "RETURN Employee.name ORDER BY Employee.name", name=name)
    record = result.single()
    print(record)
    
def optional_match(tx):
    # Use OPTIONAL MATCH to find nodes that may or may not have a relationship.
    result = tx.run("OPTIONAL MATCH (a:Person)-[r:KNOWS]->(b:Person) RETURN a.name, b.name")
    for record in result:
        print(f"{record['a.name']} knows {record['b.name']}")

def where_clause(tx):
    # Use WHERE clause to filter nodes.
    result = tx.run("MATCH (a:Person) WHERE a.age > 25 RETURN a.name, a.age")
    for record in result:
        print(f"{record['a.name']} is {record['a.age']} years old")

def count_function(tx):
    # Use COUNT function to count nodes.
    result = tx.run("MATCH (a:Person) RETURN COUNT(a) as count")
    record = result.single()
    print(f"Total number of Person nodes: {record['count']}")

# Use the session to read the transactions.    
with driver.session() as session:
    # Find and print all nodes.
    session.execute_read(find_all_nodes)
    # Find and print who works with Grace.
    session.execute_read(find_relations, "Grace")
    # Optional match example
    session.execute_read(optional_match)
    # Where clause example
    session.execute_read(where_clause)
    # Count function example
    session.execute_read(count_function)



# + vscode={"languageId": "ruby"}
def plot_graph(results):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges from the query results
    for record in result:
        G.add_node(record['from'])
        G.add_node(record['to'])
        G.add_edge(record['from'], record['to'], label=record['rel'])

    # Draw the graph
    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='gray', font_size=15, font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=12)
    plt.title("Neo4j Graph Visualization")
    plt.show()
