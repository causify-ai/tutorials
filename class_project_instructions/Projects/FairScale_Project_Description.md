### Project 1: **Scalable Text Classification with FairScale**
- **Difficulty:** 1
- **Tech Description:** FairScale will be used to implement model parallelism to efficiently scale a pre-trained transformer model for text classification tasks.
- **Project Idea:** The goal of this project is to classify news articles into predefined categories (e.g., politics, sports, technology) using a pre-trained transformer model. By leveraging FairScale's model parallelism, students will implement a scalable solution that allows them to handle larger datasets without running into memory constraints. The project will involve fine-tuning a pre-trained BERT model on the AG News dataset, evaluating its performance, and demonstrating the benefits of using FairScale for efficient model training.
- **Python libs:** PyTorch, FairScale, Transformers, Pandas, Scikit-learn
- **Is it Free?** Yes, all libraries and datasets used are free and open-source.
- **Relevant tool (FairScale) related Resource Links:** 
  - [FairScale GitHub Repository](https://github.com/facebookresearch/fairscale)
  - [AG News Dataset](https://www.kaggle.com/amananandrai/ag-news-classification-dataset)

---

### Project 2: **Distributed Anomaly Detection in Time-Series Data**
- **Difficulty:** 2
- **Tech Description:** FairScale will facilitate distributed training of an autoencoder model to detect anomalies in large time-series datasets.
- **Project Idea:** This project aims to develop a scalable anomaly detection system using an autoencoder trained on the Yahoo Finance stock price dataset. Students will utilize FairScale to distribute the training process across multiple GPUs, enabling them to efficiently learn representations of normal behavior in stock prices. The project will include data preprocessing, model training, and evaluation of the autoencoder's ability to identify outliers in the time-series data.
- **Python libs:** PyTorch, FairScale, Numpy, Pandas, Matplotlib
- **Is it Free?** Yes, all libraries and datasets are freely available.
- **Relevant tool (FairScale) related Resource Links:** 
  - [FairScale Documentation](https://fairscale.readthedocs.io/en/latest/)
  - [Yahoo Finance Stock Price Dataset](https://www.kaggle.com/datasets/sbhatti/stock-market-data)

---

### Project 3: **Scalable Image Segmentation with FairScale**
- **Difficulty:** 3
- **Tech Description:** FairScale will be employed to implement gradient checkpointing and model parallelism for training a segmentation model on large image datasets.
- **Project Idea:** The objective of this project is to perform image segmentation on the Cityscapes dataset, which contains high-resolution images of urban scenes. By leveraging FairScale’s features, students will implement a U-Net architecture with gradient checkpointing to optimize memory usage during training. The project will involve data augmentation, model training, and evaluation of segmentation performance, demonstrating how FairScale can enhance model efficiency for complex image tasks.
- **Python libs:** PyTorch, FairScale, OpenCV, Matplotlib, Albumentations
- **Is it Free?** Yes, all libraries and datasets are free to use.
- **Relevant tool (FairScale) related Resource Links:** 
  - [FairScale Examples](https://fairscale.readthedocs.io/en/latest/examples.html)
  - [Cityscapes Dataset](https://www.cityscapes-dataset.com/)

