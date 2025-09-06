**Description**

In this project, students will utilize igraph, a powerful library for creating and analyzing graphs and networks, to explore various data science problems involving network structures. igraph offers features for graph creation, manipulation, visualization, and analysis, making it suitable for tasks such as community detection, centrality measures, and network dynamics.

Technologies Used
igraph

- Provides a comprehensive set of functions for graph creation and manipulation.
- Supports various algorithms for network analysis, including community detection and shortest path calculations.
- Allows for advanced visualization of networks with customizable layouts and styles.

---

### Project 1: Social Network Analysis of Movie Ratings
**Difficulty**: 1 (Easy)  
**Project Objective**: Analyze a social network of movie ratings to identify influential users and communities based on their interactions and ratings, optimizing for community detection.

**Dataset Suggestions**:  
- Use the "MovieLens 100K" dataset available on Kaggle.  
- Link: [MovieLens 100K](https://grouplens.org/datasets/movielens/100k/)

**Tasks**:
- **Data Preprocessing**: Load and clean the MovieLens dataset, focusing on user-item interactions.
- **Graph Construction**: Create a bipartite graph where users and movies are represented as nodes, and ratings as edges.
- **Community Detection**: Apply algorithms (e.g., Louvain method) to detect communities within the user network based on their ratings.
- **Centrality Analysis**: Calculate centrality measures (e.g., degree, betweenness) to identify influential users in the network.
- **Visualization**: Visualize the constructed graph and detected communities using igraph’s plotting capabilities.

---

### Project 2: Analyzing Twitter Interaction Networks
**Difficulty**: 2 (Medium)  
**Project Objective**: Investigate the interaction network among Twitter users discussing a specific topic, optimizing for the detection of influential users and topic communities.

**Dataset Suggestions**:  
- Use the "Twitter API" to collect tweets related to a specific hashtag (e.g., #ClimateChange) and build a network based on retweets and mentions.  
- Ensure to follow Twitter's API guidelines for free access.

**Tasks**:
- **Data Collection**: Use Tweepy to collect tweets and user interactions based on the chosen hashtag.
- **Graph Construction**: Build a directed graph where nodes are users and edges represent retweets or mentions.
- **Community Detection**: Use clustering algorithms (e.g., Girvan-Newman) to identify communities discussing the topic.
- **Influencer Identification**: Analyze the network to find key influencers using centrality measures.
- **Network Dynamics**: Explore how the network evolves over time by comparing snapshots of the graph at different intervals.

---

### Project 3: Anomaly Detection in Network Traffic Data
**Difficulty**: 3 (Hard)  
**Project Objective**: Develop a system to detect anomalies in network traffic using graph-based methods, optimizing for the identification of unusual patterns indicating potential security threats.

**Dataset Suggestions**:  
- Utilize the "UNSW-NB15" dataset available on Kaggle, which contains network traffic data with labeled attacks.  
- Link: [UNSW-NB15](https://www.kaggle.com/datasets/mohammadami/unsw-nb15-dataset)

**Tasks**:
- **Data Preprocessing**: Clean and preprocess the UNSW-NB15 dataset to extract relevant features for graph construction.
- **Graph Construction**: Create a graph where nodes represent devices and edges represent communication sessions, weighted by traffic volume.
- **Anomaly Detection**: Implement graph-based anomaly detection techniques (e.g., spectral clustering) to identify unusual traffic patterns.
- **Evaluation**: Assess the performance of the anomaly detection using metrics such as precision, recall, and F1-score.
- **Visualization**: Visualize the detected anomalies and the underlying network structure to interpret the results effectively.

**Bonus Ideas (Optional)**: 
- For Project 1, compare results with traditional clustering methods (e.g., K-means).
- For Project 2, extend the analysis to include sentiment analysis of tweets to understand community sentiments.
- For Project 3, explore integrating machine learning models to enhance anomaly detection accuracy.

