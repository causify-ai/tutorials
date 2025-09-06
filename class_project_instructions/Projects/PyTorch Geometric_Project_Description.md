**Description**

In this project, students will utilize PyTorch Geometric, a library built on PyTorch for deep learning on irregularly structured data such as graphs. It provides a range of functionalities, including graph neural networks (GNNs), message passing, and various pooling layers, which allow for the efficient processing and analysis of graph data.

Technologies Used
PyTorch Geometric

- Facilitates the implementation of graph neural networks (GNNs) with intuitive APIs.
- Supports various types of graph data and operations, including convolutional layers for graphs.
- Provides a rich set of datasets and benchmark tasks for experimentation.

---

### Project 1: Social Network Analysis (Difficulty: 1)

**Project Objective:**  
Analyze a social network graph to identify influential nodes (users) using centrality measures and classification techniques.

**Dataset Suggestions:**  
- Use the "Facebook Social Network" dataset available on Kaggle. 

**Tasks:**
- **Data Ingestion:**
  - Load the Facebook social network dataset and construct a graph using PyTorch Geometric.
  
- **Graph Preprocessing:**
  - Normalize the graph and compute node features such as degree centrality and betweenness centrality.
  
- **Node Classification:**
  - Implement a simple Graph Neural Network (GNN) to classify nodes based on their features.
  
- **Evaluation:**
  - Evaluate the model's performance using accuracy and F1-score metrics on a hold-out test set.

- **Visualization:**
  - Visualize the graph and highlight influential nodes using Matplotlib.

---

### Project 2: Molecular Property Prediction (Difficulty: 2)

**Project Objective:**  
Develop a model to predict molecular properties (e.g., solubility) based on their chemical structure represented as graphs.

**Dataset Suggestions:**  
- Use the "Molecular Graphs" dataset from the MoleculeNet benchmark available on GitHub.

**Tasks:**
- **Data Preparation:**
  - Load molecular graphs and their properties using PyTorch Geometric’s dataset utilities.
  
- **Feature Engineering:**
  - Extract relevant features from molecular graphs, including atom types and bond types.
  
- **Model Development:**
  - Build a GNN model that predicts molecular properties based on the graph representation.
  
- **Hyperparameter Tuning:**
  - Optimize model hyperparameters using cross-validation techniques.
  
- **Model Evaluation:**
  - Assess the model's performance using regression metrics like Mean Absolute Error (MAE) and R² score.

---

### Project 3: Traffic Flow Prediction (Difficulty: 3)

**Project Objective:**  
Create a predictive model for traffic flow in a city using a spatio-temporal graph representation of traffic data.

**Dataset Suggestions:**  
- Use the "PEMS Traffic Flow" dataset available on Kaggle, which contains traffic flow data at various sensors over time.

**Tasks:**
- **Graph Construction:**
  - Construct a dynamic graph where nodes represent traffic sensors and edges represent road connections.
  
- **Temporal Feature Integration:**
  - Incorporate time-series data into the graph structure to capture temporal dependencies.
  
- **GNN Architecture:**
  - Implement a Spatio-Temporal Graph Convolutional Network (ST-GCN) to model traffic flow prediction.
  
- **Training and Validation:**
  - Train the model on historical traffic data and validate its performance on a separate test set.
  
- **Performance Metrics:**
  - Evaluate the model using metrics like Root Mean Square Error (RMSE) and compare against baseline models.

**Bonus Ideas (Optional):**  
- Implement a real-time traffic prediction system using live traffic data from OpenTraffic API.
- Compare the performance of different GNN architectures (e.g., GAT, GraphSAGE) on the same dataset.
- Explore the impact of additional features like weather conditions on traffic flow predictions.

