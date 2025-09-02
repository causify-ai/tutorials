### Project Brief: Real-Time Bitcoin Price Prediction with Triton

- **Difficulty**: 3
- **Tech Description**: Triton is a high-performance inference server that can optimize and serve machine learning models, enabling real-time predictions with low latency.
- **Project Idea**: Build a real-time Bitcoin price prediction system that ingests live market data from multiple cryptocurrency exchanges using Triton for model inference. The system will utilize a recurrent neural network (RNN) model to forecast short-term price movements based on historical price data and trading volume.
- **Python libs**: 
  - `tritonclient` for interacting with Triton Inference Server
  - `pandas` for data manipulation
  - `numpy` for numerical operations
  - `tensorflow` or `pytorch` for building the RNN model
  - `requests` for API calls to cryptocurrency exchanges
  - `asyncio` for handling asynchronous data ingestion
- **Is it Free?**: Triton is open-source and free to use, but hosting may incur costs depending on the infrastructure.
- **Relevant tool (Triton) related Resource Links**:
  - [NVIDIA Triton Inference Server Documentation](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html)
  - [Triton GitHub Repository](https://github.com/triton-inference-server/server)
  - [NVIDIA Developer Blog on Triton](https://developer.nvidia.com/blog/nvidia-triton-inference-server/)

