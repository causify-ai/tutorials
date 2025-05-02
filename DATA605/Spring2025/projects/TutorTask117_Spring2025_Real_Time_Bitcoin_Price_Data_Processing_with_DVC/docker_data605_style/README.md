# 🗃️ Real-Time Bitcoin Data Processing with DVC

**Difficulty**: Medium (Level 2)  
**Tools**: DVC, requests, pandas, matplotlib, CoinGecko API

---

## 🧠 Project Description

This project introduces a robust and reproducible system for real-time Bitcoin data collection and analysis using **DVC (Data Version Control)**.

By integrating **data versioning**, **pipeline automation**, and **experiment tracking**, the system enables scalable management of time series data and supports flexible experimentation on Bitcoin price trends.

---

## ⚙️ Technology Overview

### 🧩 What is DVC?

**DVC (Data Version Control)** is an open-source version control system tailored for managing:
- Large datasets
- Machine learning experiments
- Data processing pipelines

It works alongside Git and helps you version not only code, but also **data**, **models**, and **metrics**.

#### 🔑 Key Features:
- **Data Management**: Use lightweight `.dvc` metafiles instead of storing large data in Git
- **Reproducibility**: Define clear stages with reproducible commands and input/output dependencies
- **Experiment Tracking**: Run experiments and compare outputs over time
- **Pipeline Automation**: Automate ingestion, processing, and analysis with `dvc.yaml` pipelines

---

## 📌 Project Workflow

### 1. 📥 Data Ingestion
- Fetch real-time Bitcoin prices using [CoinGecko API](https://www.coingecko.com/en/api)
- Use the `requests` library for HTTP API calls at fixed intervals
- Store ingested data in a `.csv` file tracked via DVC

### 2. 🔄 Data Processing
- Use `pandas` to process and analyze time series data
- Perform simple rolling averages or volatility tracking
- Use `matplotlib` to generate trend plots

### 3. ⚙️ DVC Pipeline Setup
- Define pipeline stages in `dvc.yaml`:
  - `stage 1`: Data ingestion (API pull)
  - `stage 2`: Data cleaning & transformation
  - `stage 3`: Data analysis & plotting
- Each stage automatically tracks input/output dependencies for reproducibility

### 4. 🧪 Experiment Tracking
- Change analysis logic, frequency of data pulls, or time windows
- Use `dvc exp run` and `dvc exp show` to compare results
- Revert, modify, or checkpoint versions as needed

---

## 📚 Useful Resources

- [📘 DVC Documentation](https://dvc.org/doc)
- [📘 CoinGecko API Docs](https://www.coingecko.com/en/api)
- [📘 Requests Docs](https://docs.python-requests.org/en/latest/)
- [📘 Pandas Docs](https://pandas.pydata.org/docs/)
- [📘 Matplotlib Docs](https://matplotlib.org/stable/contents.html)

---

## 💸 Is It Free?

Yes! Everything used in this project is free and open-source:
- **DVC**: Free to install and use
- **Python libraries**: All are open-source
- **CoinGecko API**: Public access is free with usage limits

---

## 🐍 Python Dependencies

Install all necessary libraries:

```bash
pip install dvc
pip install requests
pip install pandas
pip install matplotlib