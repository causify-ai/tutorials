### Project 1: Hyperparameter Optimization for Machine Learning Models
- **Difficulty**: 1
- **Tech Description**: BoTorch is utilized for efficient Bayesian optimization to tune hyperparameters of machine learning models.
- **Project Idea**: The goal of this project is to optimize the hyperparameters of a regression model (e.g., Random Forest or Support Vector Regression) using BoTorch. The student will define a search space for hyperparameters and use the tool to iteratively evaluate model performance based on a validation dataset. The project will involve comparing the performance of the optimized model against default hyperparameters and analyzing the impact of different hyperparameter settings on model accuracy. A dataset such as the California Housing dataset from the UCI Machine Learning Repository will be used.
- **Python libs**: BoTorch, PyTorch, Scikit-learn, NumPy, Pandas
- **Is it Free?**: Yes, BoTorch is an open-source library available for free.
- **Relevant tool (BoTorch) related Resource Links**: [BoTorch Documentation](https://botorch.org/docs/), [UCI California Housing Dataset](https://archive.ics.uci.edu/ml/datasets/California+Housing+Prices)

---

### Project 2: Multi-Objective Optimization in Drug Design
- **Difficulty**: 2
- **Tech Description**: BoTorch is applied to perform multi-objective Bayesian optimization to identify optimal drug compounds based on desired properties.
- **Project Idea**: This project aims to optimize the properties of drug compounds by balancing efficacy and toxicity using BoTorch's multi-objective optimization capabilities. The student will use a dataset of drug compounds with chemical descriptors and their corresponding efficacy and toxicity scores. By defining the objectives, the student will explore the Pareto front to identify compounds that achieve a good balance between the two objectives. The project will involve visualizing the results and discussing the trade-offs in drug design.
- **Python libs**: BoTorch, PyTorch, Matplotlib, Scikit-learn, RDKit
- **Is it Free?**: Yes, all the mentioned libraries and datasets are freely available.
- **Relevant tool (BoTorch) related Resource Links**: [BoTorch Multi-Objective Optimization](https://botorch.org/docs/multi_objective), [ChEMBL Database](https://www.ebi.ac.uk/chembl/)

---

### Project 3: Adaptive Experimental Design for Environmental Monitoring
- **Difficulty**: 3
- **Tech Description**: BoTorch is used to create an adaptive experimental design framework for optimizing sampling locations in environmental monitoring.
- **Project Idea**: The objective of this project is to optimize the placement of sensors in a hypothetical environmental monitoring scenario using adaptive sampling techniques enabled by BoTorch. The student will simulate a spatial model of pollutant dispersion and use existing data (e.g., air quality data from the OpenAQ platform) to inform the sampling strategy. The project will involve defining a utility function to maximize information gain and iteratively updating the design based on observed data. The results will be analyzed to demonstrate the efficiency of the adaptive design compared to random sampling.
- **Python libs**: BoTorch, PyTorch, NumPy, SciPy, Matplotlib
- **Is it Free?**: Yes, all tools and datasets used in this project are freely available.
- **Relevant tool (BoTorch) related Resource Links**: [BoTorch Adaptive Experimental Design](https://botorch.org/docs/adaptive), [OpenAQ API](https://docs.openaq.org/)

