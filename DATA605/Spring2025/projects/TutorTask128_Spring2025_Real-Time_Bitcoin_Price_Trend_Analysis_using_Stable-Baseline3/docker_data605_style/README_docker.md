# 🐳 Docker Instructions + Project Progress Report

This project is part of the DATA605 class and demonstrates:

📊 **Real-Time Bitcoin Price Trend Analysis using Stable-Baselines3**  
🧪 Branch: `TutorTask128_Spring2025_Real-Time_Bitcoin_Price_Trend_Analysis_using_Stable-Baseline3`

---

## ✅ Project Goal

Build a reproducible reinforcement learning system that predicts Bitcoin price trends using:

- Real-time Bitcoin data (via CoinGecko API)
- Custom environment built with **Gymnasium**
- Models trained using **Stable-Baselines3**

---

## 📦 What’s Done So Far (25% Milestone)

### ✅ Docker Environment
- [x] Docker image built using `docker_data605_style`
- [x] Runs Python, Jupyter, Stable-Baselines3, and required libraries

### ✅ GitHub Branch & Organization
- [x] Branch created: `TutorTask128_Spring2025_Real-Time_Bitcoin_Price_Trend_Analysis_using_Stable-Baseline3`
- [x] All files committed and pushed to correct folder structure

### ✅ Utility Module (`bitcoin_rl_utils.py`)
- [x] Created function `fetch_bitcoin_data()` to fetch real-time data using CoinGecko API
- [x] Handles timestamp parsing and returns clean DataFrame

### ✅ API Notebook (`bitcoin_rl_API.ipynb`)
- [x] Calls utility function to fetch Bitcoin prices
- [x] Generates time-series plot of price trends over 3 days

### ✅ API Markdown (`bitcoin_rl_API.md`)
- [x] Describes purpose, structure, and output of API module
- [x] Explains function usage and output formatting

### ✅ Git Hygiene
- [x] Old analysis file (`bitcoin_rl_analysis.ipynb`) removed
- [x] Version control set up with future-ready branching strategy

---

## 🛠️ How to Run This Project (Docker Setup)

### 1️⃣ Clone the Repo and Switch to the Project Branch

```bash
git clone https://github.com/causify-ai/tutorials.git
cd tutorials
git checkout TutorTask128_Spring2025_Real-Time_Bitcoin_Price_Trend_Analysis_using_Stable-Baseline3
