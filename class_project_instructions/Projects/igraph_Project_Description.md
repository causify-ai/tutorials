### Project 1: Social Network Analysis of Twitter Users
- **Difficulty**: 1
- **Tech Description**: Utilize igraph to analyze and visualize the structure of a Twitter user network based on follower relationships.
- **Project Idea**: The goal of this project is to explore the connections and influence among Twitter users within a specific domain (e.g., environmental activism). By querying the Twitter API, students will gather data on users, their followers, and their tweets. Using igraph, they will create a graph representation of the network, calculate centrality measures, and visualize key influencers. The analysis will highlight how information spreads within the network and identify potential hubs of activity.
- **Python libs**: igraph, tweepy, pandas, matplotlib, networkx
- **Is it Free?**: Yes, the Twitter API provides free access to a limited number of requests, allowing for data collection without cost.
- **Relevant tool (igraph) related Resource Links**: [igraph Documentation](https://igraph.org/python/), [Twitter API Documentation](https://developer.twitter.com/en/docs/twitter-api)

---

### Project 2: Community Detection in Academic Collaboration Networks
- **Difficulty**: 2
- **Tech Description**: Implement igraph to detect communities in a collaboration network of academic papers based on co-authorship.
- **Project Idea**: This project aims to analyze the collaboration patterns among researchers in a specific field (e.g., machine learning). Students will download co-authorship data from the OpenCitations API or similar sources. Using igraph, they will construct a graph where nodes represent authors and edges represent co-authorship. The project will involve applying community detection algorithms to identify clusters of researchers who frequently collaborate, along with visualizing these communities to understand collaboration dynamics.
- **Python libs**: igraph, requests, pandas, seaborn, matplotlib
- **Is it Free?**: Yes, OpenCitations offers free access to their dataset, enabling students to perform the analysis without incurring costs.
- **Relevant tool (igraph) related Resource Links**: [igraph Community Detection](https://igraph.org/python/doc/tutorial/tutorial.html#community-detection), [OpenCitations API](https://opencitations.net/)

---

### Project 3: Anomaly Detection in Network Traffic
- **Difficulty**: 3
- **Tech Description**: Use igraph to model network traffic and detect anomalies based on graph-based features.
- **Project Idea**: The objective of this project is to analyze network traffic data to identify unusual patterns that may indicate security threats. Students will use the CICIDS 2017 dataset, which contains labeled network traffic data. They will construct a graph representation of the traffic, where nodes represent devices and edges represent communication events. Using igraph, they will extract features such as degree centrality and clustering coefficients, then apply anomaly detection techniques to identify suspicious activities. The project will culminate in visualizing the anomalies within the network graph.
- **Python libs**: igraph, pandas, scikit-learn, numpy, matplotlib
- **Is it Free?**: Yes, the CICIDS 2017 dataset is publicly available for research purposes, allowing students to access the data without cost.
- **Relevant tool (igraph) related Resource Links**: [igraph Anomaly Detection](https://igraph.org/python/doc/tutorial/tutorial.html#anomaly-detection), [CICIDS 2017 Dataset](https://www.unb.ca/cic/datasets/malmem-2020.html)

