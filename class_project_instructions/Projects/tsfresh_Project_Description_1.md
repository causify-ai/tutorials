### Title
Real-Time Anomaly Detection in Bitcoin Transactions using tsfresh

### Difficulty
3

### Tech Description
Utilize tsfresh for extracting relevant features from time-series data of Bitcoin transactions to detect anomalies in real-time.

### Project Idea
- Ingest real-time Bitcoin transaction data from a streaming source (e.g., WebSocket API).
- Use tsfresh to extract time-series features from the transaction data.
- Implement an anomaly detection model to identify suspicious transactions based on the extracted features.

### Python libs
- `tsfresh` for feature extraction
- `pandas` for data manipulation
- `numpy` for numerical operations
- `scikit-learn` for machine learning models
- `websocket-client` for real-time data ingestion
- `matplotlib` for visualization

### Is it Free?
Yes, all mentioned libraries are open-source and free to use.

### Relevant tool (XYZ) related Resource Links
- [tsfresh Documentation](https://tsfresh.readthedocs.io/en/latest/)
- [tsfresh GitHub Repository](https://github.com/blue-yonder/tsfresh)
- [Anomaly Detection with tsfresh](https://tsfresh.readthedocs.io/en/latest/text/usage.html#anomaly-detection)

