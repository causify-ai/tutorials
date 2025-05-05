# 📈 Real-Time Bitcoin Causal Analysis with DoWhy

**Difficulty**: Medium (Level 2)  
**Tools**: DoWhy, pandas, matplotlib, CoinGecko API

---

## 🧠 Description

This project aims to build a Python-based big data system that continuously ingests real-time Bitcoin price data and applies **causal inference techniques using DoWhy**.

The goal is to evaluate the **impact of market events** (e.g., news, regulations) on Bitcoin prices by defining causal relationships and rigorously testing their robustness using statistical methods.

---

## ⚙️ Technology Overview

### 🔍 DoWhy Library
- Python package for **causal inference** combining graphical models and potential outcomes framework.
- Allows modeling using **DAGs (Directed Acyclic Graphs)**.
- Supports **counterfactual analysis** and **refutation tests**.

### 🐍 Python Stack
- **pandas** – for data wrangling and time series formatting  
- **matplotlib / seaborn** – for beautiful data visualizations  
- **requests / websockets** – to fetch real-time Bitcoin price data  
- **DoWhy** – to perform causal estimation and validation  

---

## 📌 Project Milestones

### 1. 🛠️ Data Ingestion
- Fetch real-time Bitcoin prices using CoinGecko API.
- Optionally handle streaming data with `websockets`.

### 2. 🧹 Data Processing
- Use `pandas` to clean and structure data into a time series format.
- Handle missing values and align timestamps.

### 3. 🔗 Causal Model Setup
- Define:
  - **Treatment**: e.g., a market regulation or announcement  
  - **Outcome**: Bitcoin price change  
  - **Confounders**: trading volume, market sentiment, etc.
- Represent model as a **DAG**.

### 4. 📊 Apply DoWhy
- Use DoWhy to:
  - Estimate treatment effects  
  - Run **refutation tests** to validate model assumptions  
  - Analyze counterfactuals

### 5. 📈 Visualization & Reporting
- Visualize causal graphs and results using `matplotlib`/`seaborn`.
- Compile a summary report:
  - Estimated causal effects  
  - Graph structure  
  - Refutation outcomes  

---

## 🔗 Useful Resources

- [📚 DoWhy Documentation](https://microsoft.github.io/dowhy/)
- [📚 pandas Documentation](https://pandas.pydata.org/docs/)
- [📚 matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [📚 CoinGecko API](https://www.coingecko.com/en/api)

---

## 💸 Is It Free?

Yes, everything used is open-source and freely available:
- **DoWhy**, **pandas**, **matplotlib**, and **seaborn** are all open-source libraries.
- **CoinGecko API** offers free access with public rate limits.

---

## 📦 Python Dependencies

To install all required packages:

```bash
pip install dowhy pandas matplotlib seaborn requests