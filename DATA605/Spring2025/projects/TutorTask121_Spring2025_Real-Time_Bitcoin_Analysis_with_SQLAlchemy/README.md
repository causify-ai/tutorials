# Real-Time Bitcoin Analysis with SQLAlchemy

##  Overview

This project implements an end-to-end Bitcoin price forecasting system using real-time data. It demonstrates how to:

- Fetch Bitcoin price data using the public **CoinGecko API**
- Store and manage data using **SQLAlchemy** and **SQLite**
- Automate ingestion of both historical and real-time price data
- Perform **feature engineering**, **exploratory data analysis**, and **model training**
- Evaluate and visualize forecasting results using **Linear Regression** and **Random Forest**

The project is structured like a professional open-source tutorial with clean utility modules, Jupyter notebooks, and full Docker integration.

---

##  Technologies Used

| Tool | Purpose |
|------|---------|
| **Docker** | Environment setup, dependency isolation |
| **SQLAlchemy** | Database schema definition and ORM |
| **SQLite** | Local storage of historical and real-time data |
| **CoinGecko API** | Public REST API for cryptocurrency prices |
| **pandas / matplotlib** | Data processing and visualization |
| **scikit-learn** | Regression models and metrics |
| **Jupyter Notebook** | Interactive workflow for ingestion, modeling, and visualization |

---

##  Project Structure

```plaintext
.
├── SQLAlchemy_utils.py             # Utility functions: DB, API wrappers
├── SQLAlchemy.API.ipynb           # Demonstrates API and DB usage
├── SQLAlchemy.API.md              # Explains API layer and design
├── SQLAlchemy.example.ipynb       # Full end-to-end notebook: ingestion → model
├── SQLAlchemy.example.md          # Written explanation of modeling example
├── docker_build.sh                # Script to build Docker container
├── docker_bash.sh                 # Script to open bash shell inside container
├── docker_jupyter.sh              # Script to start Jupyter notebook in container
└── README.md                      # Project overview and instructions


