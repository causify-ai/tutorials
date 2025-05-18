# 📈 Bitcoin Real-Time Analysis PyNaCl
# By Dhanush Vasa (121227645)

A modular and secure Python-based platform to ingest, encrypt, store, and analyze real-time Bitcoin price data using Binance APIs. Built with extensibility in mind, it supports encrypted storage, hourly forecasting, and visual insights via dashboards.

---

## 🚀 Features

- ⏱ Real-time Bitcoin price ingestion (via Binance WebSocket)
- 🔐 RSA encryption of sensitive data
- 🗄 Encrypted storage using SQLite
- 📊 Time-series and volatility analysis
- 📈 Interactive dashboards using Plotly Dash
- 🐳 Dockerized for consistent deployment

---

## 🛠 Tech Stack

### 📦 Programming & Libraries
- **Python 3.9+** – Core language
- **PyNaCl** – Public-key encryption & digital signatures
- **Pandas** – Time-series data analysis
- **Requests** – API interaction for real-time Bitcoin data
- **Plotly Dash** – Interactive data visualization
- **SQLite** – Lightweight encrypted data storage

### 🐳 DevOps & Deployment
- **Docker** – Containerized development environment
- **AWS** – Dashboard hosting and deployment

### 🔐 Cryptography
- **Curve25519 + XSalsa20 + Poly1305** – Secure encryption via PyNaCl’s `SealedBox`
- **Digital Signatures** – For data integrity verification

### 📈 Analytics
- **ARIMA Models** – Predictive modeling for Bitcoin price trends

---

## 🧩 Project Structure
```
bitcoin_analysis_project/
├── crypto/                  # Encryption utilities
│   └── encrypt.py           # Functions for encrypting and decrypting data
├── docker_data605_style/    # Docker setup and deployment scripts
├── static/                  # Static assets (e.g., generated plots)
├── main.py                  # Main script to orchestrate data ingestion and storage
├── generate_keys.py         # Script to generate RSA key pairs
├── bitcoin_analysis.db      # SQLite database containing encrypted Bitcoin price data
├── requirements.txt         # List of Python dependencies
└── README.md                # Project documentation and usage instructions
```
---

## ⚙️ Getting Started

## 🐳 Docker SetupDocker (Recomended)
To use the pre-configured Docker environment:

### 1. Clone & Install

```bash
git clone "project"
cd bitcoin_analysis_project
python3 -m venv PYNACL_venv
source PYNACL_venv/bin/activate
pip install -r requirements.txt
```
---
### How to run Docker Clean
### Step 1: Make It Executable
```bash
cd docker_data605_style
```

```bash
chmod +x docker_clean.sh
```

### Step 2: Run It Again
```bash
./docker_clean.sh
```
### How to run Docker Build
### Step 1: Make It Executable
```bash
chmod +x docker_build.sh
```

### Step 2: Run It Again
```bash
./docker_build.sh
```

### How to run Docker Run
### Step 1: Make It Executable
```bash
chmod +x docker_run.sh
```

### Step 2: Run It Again
```bash
./docker_run.sh
```

## Access to DashBoard

```Locally
http://localhost:8050
```

```AWS
http://13.203.213.228:8050/
```

## ✨ Features & Functionality

### 🔄 Real-Time Bitcoin Data Ingestion
- Connects to Binance WebSocket API to stream live Bitcoin trade data
- Captures timestamp, price, and volume at sub-minute intervals

### 🔐 End-to-End Encryption using PyNaCl
- Public-key encryption (Curve25519, XSalsa20, Poly1305) for all incoming trade data
- Ensures that sensitive price data remains confidential during transmission and storage

### 💾 Encrypted Data Storage
- Encrypted records are stored in a local **SQLite** database
- Structure supports fast read/write and can scale for historical analysis

### 📉 Time-Series Analysis
- Real-time and batch processing of price data
- Includes moving averages, volatility analysis, and basic trend detection

### 📊 Forecasting with ARIMA
- Implements Auto-Regressive Integrated Moving Average (ARIMA) for short-term price prediction
- Extensible to other models like LSTM, Prophet, etc.

### ✅ Data Integrity Verification
- Uses digital signatures to verify the authenticity of stored and transmitted data
- Prevents tampering or replay attacks on financial records

### 📈 Interactive Dashboard
- Built with Plotly Dash for dynamic visualizations
- Shows live price trends, volatility graphs, and forecast overlays

### ☁️ Deployment Ready
- Docker scripts included for local development
- Successfully deployed to **Streamlit Cloud** and **AWS**

## 🔐 Data Security

All trade data is encrypted using [NaCl](https://nacl.cr.yp.to/) cryptography before storage. Specifically, it uses public-key encryption (e.g., `SealedBox`) based on Curve25519 for key exchange, XSalsa20 for encryption, and Poly1305 for authentication. This ensures strong confidentiality and integrity of sensitive financial data.

## 📊 Sample Data Schema

| Timestamp          | Price     | Volume   | Encrypted |
|--------------------|-----------|----------|-----------|
| 2025-05-17 10:45AM | 67850.23  | 0.0031   | ✅        |
| 2025-05-17 10:46AM | 67852.10  | 0.0050   | ✅        |
| 2025-05-17 10:47AM | 67855.85  | 0.0024   | ✅        |

## 🧠 Roadmap

This project focuses on real-time Bitcoin price analysis with strong data security using PyNaCl. The roadmap outlines a step-by-step approach to building the complete system:

### ✅ Phase 1: Project Setup & Dependencies
- [x] Define project structure and objectives
- [x] Install required Python libraries: `pynacl`, `requests`, `pandas`, `plotly`

### 🔄 Phase 2: Real-Time Data Ingestion
- [x] Connect to a public Bitcoin API (Binance )
- [x] Fetch live price and volume data at regular intervals

### 🔐 Phase 3: Secure Data Transmission & Storage
- [x] Use PyNaCl's public-key encryption to encrypt trade data
- [x] Store encrypted data in a local SQLite database

### 📈 Phase 4: Time-Series Analysis
- [x] Use Pandas to compute moving averages and volatility
- [x] Add predictive models (ARIMA)

### ✍️ Phase 5: Data Integrity & Verification
- [x] Implement digital signatures to verify authenticity of stored records

### 📊 Phase 6: Visualization Dashboard
- [x] Create interactive plots using Plotly Dash
- [x] Deploy dashboard to AWS
