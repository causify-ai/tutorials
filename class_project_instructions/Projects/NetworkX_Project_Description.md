### Project 1: Social Network Analysis of Twitter Influencers
- **Difficulty**: 1
- **Tech Description**: NetworkX will be used to create and analyze the social graph of Twitter influencers based on their follower relationships.
- **Project Idea**: This project aims to explore the structure of influence within Twitter by analyzing a specific niche (e.g., environmental activists). Students will collect follower data using the Twitter API and construct a directed graph where nodes represent users and edges represent follower relationships. The goal is to identify key influencers, measure their centrality, and visualize the network to understand how information spreads within this community.
- **Python libs**: NetworkX, Tweepy, Matplotlib, Pandas
- **Is it Free?**: Yes, the Twitter API provides free access to public tweets and user data under certain rate limits.
- **Relevant tool (NetworkX) related Resource Links**: 
  - [NetworkX Documentation](https://networkx.org/documentation/stable/)
  - [Twitter API Documentation](https://developer.twitter.com/en/docs/twitter-api)

---

### Project 2: Anomaly Detection in Transportation Networks
- **Difficulty**: 2
- **Tech Description**: NetworkX will be utilized to model transportation networks and identify anomalies in traffic patterns.
- **Project Idea**: This project focuses on analyzing public transportation data (e.g., bus routes and schedules) from the General Transit Feed Specification (GTFS). Students will construct a graph representing the transportation network, where nodes are stops and edges are routes. They will implement algorithms to detect anomalies in traffic patterns, such as unusual delays or route deviations, using metrics like clustering coefficients and shortest path analysis. The findings can help improve operational efficiency.
- **Python libs**: NetworkX, Pandas, NumPy, Matplotlib, GTFS library (like gtfslib)
- **Is it Free?**: Yes, GTFS data is publicly available from various transit agencies.
- **Relevant tool (NetworkX) related Resource Links**: 
  - [NetworkX Anomaly Detection](https://networkx.org/documentation/stable/reference/algorithms/index.html#anomaly-detection)
  - [GTFS Data Specification](https://developers.google.com/transit/gtfs)

---

### Project 3: Community Detection in Academic Citation Networks
- **Difficulty**: 3
- **Tech Description**: NetworkX will be employed to analyze and visualize academic citation networks, focusing on community detection algorithms.
- **Project Idea**: This advanced project aims to analyze the citation relationships between academic papers in a specific field (e.g., machine learning). Students will use the OpenCitations API to gather citation data and construct a directed graph where nodes represent papers and edges represent citations. They will apply community detection algorithms (like Girvan-Newman or Louvain) to identify clusters of related research. The project will conclude with a visualization of the citation network and insights into how communities evolve over time.
- **Python libs**: NetworkX, Requests, Matplotlib, Pandas, Scikit-learn
- **Is it Free?**: Yes, OpenCitations provides free access to citation data.
- **Relevant tool (NetworkX) related Resource Links**: 
  - [NetworkX Community Detection](https://networkx.org/documentation/stable/reference/algorithms/community.html)
  - [OpenCitations API](https://opencitations.net/)

