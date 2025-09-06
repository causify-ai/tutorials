**Description**

In this project, students will utilize igraph, a library for creating and manipulating graphs and analyzing network structures. With its efficient algorithms and versatile visualization capabilities, igraph allows users to explore complex relationships within data. This tool is particularly useful for social network analysis, biological network studies, and any domain where relationships can be represented as graphs.

Technologies Used
igraph

- Provides efficient data structures for graph representation.
- Supports a variety of algorithms for network analysis (e.g., shortest path, community detection).
- Offers visualization features to create interactive graph representations.

---

**Project 1: Social Network Analysis of Twitter Users**  
**Difficulty**: 1 (Easy)  
**Project Objective**: Analyze the relationships between Twitter users based on their interactions (retweets, mentions) to identify influential users and community structures.

**Dataset Suggestions**: Use public Twitter datasets available on Kaggle that contain user interactions.

**Tasks**:
- Data Collection:
  - Gather Twitter interaction data (retweets, mentions) using available public datasets.
- Graph Construction:
  - Build a directed graph where nodes represent users and edges represent interactions.
- Community Detection:
  - Apply community detection algorithms to identify clusters of users with similar interests.
- Influence Analysis:
  - Calculate centrality measures (e.g., degree, betweenness) to identify influential users.
- Visualization:
  - Create visual representations of the user interactions and communities using igraph's plotting functions.

**Bonus Ideas (Optional)**:
- Compare different community detection algorithms and their effectiveness.
- Explore the temporal dynamics of user interactions over time.

---

**Project 2: Analyzing Protein-Protein Interaction Networks**  
**Difficulty**: 2 (Medium)  
**Project Objective**: Investigate the structure and properties of protein-protein interaction networks to identify key proteins and their roles in biological processes.

**Dataset Suggestions**: Utilize publicly available protein interaction datasets from databases like STRING or BioGRID.

**Tasks**:
- Data Preprocessing:
  - Clean and format the protein interaction data to create an edge list for the graph.
- Graph Construction:
  - Construct an undirected graph where nodes represent proteins and edges represent interactions.
- Network Analysis:
  - Analyze the graph using clustering coefficients and path lengths to understand network properties.
- Key Protein Identification:
  - Use centrality measures to identify essential proteins within the network.
- Visualization:
  - Visualize the protein interaction network, highlighting key proteins and interaction clusters.

**Bonus Ideas (Optional)**:
- Investigate the correlation between protein centrality and known disease associations.
- Explore the effect of adding/removing interactions on network properties.

---

**Project 3: Urban Mobility Analysis using Taxi Trip Data**  
**Difficulty**: 3 (Hard)  
**Project Objective**: Analyze urban mobility patterns by constructing a network of taxi trips in a city to identify hotspots and flow patterns.

**Dataset Suggestions**: Access public taxi trip datasets available on platforms like Kaggle or city government open data portals.

**Tasks**:
- Data Collection:
  - Retrieve and preprocess taxi trip data, including pickup and drop-off locations.
- Graph Construction:
  - Create a directed graph where nodes represent locations (pickup/drop-off points) and edges represent trips between them.
- Flow Analysis:
  - Analyze the flow of trips to identify popular routes and locations using flow metrics.
- Hotspot Identification:
  - Use clustering techniques to identify areas with high taxi trip density.
- Visualization:
  - Create a visual representation of the urban mobility network, highlighting hotspots and trip flows.

**Bonus Ideas (Optional)**:
- Compare weekday vs. weekend mobility patterns.
- Analyze the impact of events (concerts, sports) on taxi trip patterns.

