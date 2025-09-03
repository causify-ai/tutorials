### Project 1: Efficient Inference of Image Classification Models
- **Difficulty**: 1
- **Tech Description**: Apache TVM will be used to optimize pre-trained image classification models for efficient inference on edge devices.
- **Project Idea**: The goal of this project is to deploy a pre-trained image classification model (e.g., MobileNet) on a Raspberry Pi using Apache TVM to optimize the model for speed and memory usage. Students will convert the model to a format compatible with TVM, apply optimization techniques such as quantization, and measure performance improvements. The project will conclude with a comparison of inference times and accuracy before and after optimization, demonstrating the advantages of using TVM for edge applications.
- **Python libs**: tvm, numpy, torchvision, PIL, matplotlib
- **Is it Free?**: Yes, Apache TVM is open-source and freely available for anyone to use and modify.
- **Relevant tool (Apache TVM) related Resource Links**: [Apache TVM Documentation](https://tvm.apache.org/docs/index.html), [TVM Tutorials](https://tvm.apache.org/docs/tutorials/index.html)

---

### Project 2: Optimizing NLP Model for Sentiment Analysis
- **Difficulty**: 2
- **Tech Description**: Apache TVM will be utilized to optimize a pre-trained NLP model for sentiment analysis, enhancing its inference speed on cloud platforms.
- **Project Idea**: This project aims to optimize a pre-trained sentiment analysis model (e.g., DistilBERT) using Apache TVM to improve inference speed on cloud infrastructure. Students will start by deploying the model using a cloud service (like AWS Lambda) and then use TVM to optimize the model, focusing on techniques like operator fusion and kernel optimization. The project will evaluate the trade-offs between latency and accuracy and provide insights on the benefits of model optimization for real-time applications.
- **Python libs**: tvm, transformers, boto3, numpy, pandas
- **Is it Free?**: No, while Apache TVM is free, using cloud services like AWS may incur costs based on usage.
- **Relevant tool (Apache TVM) related Resource Links**: [TVM NLP Optimization Guide](https://tvm.apache.org/docs/tutorials/nlp/index.html), [Transformers Documentation](https://huggingface.co/docs/transformers/index)

---

### Project 3: Accelerating Time Series Forecasting Models
- **Difficulty**: 3
- **Tech Description**: Apache TVM will be employed to optimize time series forecasting models, enabling faster predictions for large datasets.
- **Project Idea**: The objective of this project is to optimize an LSTM-based time series forecasting model for predicting stock prices using the Yahoo Finance API. Students will first gather historical stock price data and then train a lightweight LSTM model. Using Apache TVM, they will optimize the model for performance, implementing techniques like layer fusion and mixed precision. The project will involve benchmarking the optimized model against the original in terms of prediction speed and resource efficiency, providing a comprehensive analysis of the optimization process.
- **Python libs**: tvm, numpy, pandas, keras, yfinance
- **Is it Free?**: Yes, both Apache TVM and the Yahoo Finance API are free to use.
- **Relevant tool (Apache TVM) related Resource Links**: [TVM Time Series Optimization](https://tvm.apache.org/docs/tutorials/optimization/index.html), [Yahoo Finance API Documentation](https://pypi.org/project/yfinance/)

