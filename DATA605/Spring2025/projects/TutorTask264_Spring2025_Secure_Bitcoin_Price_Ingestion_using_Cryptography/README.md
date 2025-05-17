# Secure Bitcoin Price Ingestion and Analysis System

A comprehensive system for secure Bitcoin price data collection, encryption, and analysis using Docker containerization.

## Project Overview

This project demonstrates secure handling of Bitcoin price data with:
- Real-time price ingestion from CoinGecko API
- Military-grade encryption (AES-CBC)
- Interactive visualization dashboard
- Advanced time series analysis
- Docker containerization for consistent environments

## Quick Start

1. **Build the Docker container**  
   ```bash
   ./docker_build.sh
   ```
2. **Run the container**  
   ```bash
   ./docker_bash.sh
   ```
3. **Launch Jupyter Notebook**  
   ```bash
   jupyter notebook --ip 0.0.0.0 --port 8888 --allow-root
   ```
4. **Start Streamlit Dashboard**  
   ```bash
   streamlit run streamlit_app.py
   ```

## Project Structure

\`\`\`
.
├── Dockerfile                    # Docker configuration
├── docker_build.sh               # Script to build Docker image
├── docker_bash.sh                # Script to run Docker container
├── requirements.txt              # Python dependencies
├── SecureBitcoin_utils.py        # Core utility functions
├── streamlit_app.py              # Interactive dashboard
├── SecureBitcoin.example.ipynb   # Example notebook
└── data_store.jsonl              # Encrypted data storage
\`\`\`

## Dependencies

- \`pycryptodome==3.22.0\`  
- \`requests==2.31.0\`  
- \`pandas==2.2.0\`  
- \`streamlit==1.32.0\`  
- \`plotly==5.18.0\`  
- \`statsmodels==0.14.1\`  
- \`matplotlib==3.8.0\`  

All dependencies are managed via \`requirements.txt\` and Docker.

## Docker Environment Setup

1. **Building the Image**  
   ```bash
   ./docker_build.sh
   ```
2. **Running the Container**  
   ```bash
   ./docker_bash.sh
   ```
3. **Development Environment**  
   - Jupyter Notebook server on port 8888  
   - Streamlit server on port 8501  
   - Live code via volume mount  

## Security Features

- **AES-CBC encryption** with PBKDF2 key derivation  
- **Digital signatures** (SHA-256) for integrity  
- **Encrypted JSONL storage**  

## Analysis Capabilities

- **Moving averages** (SMA, EMA)  
- **Bollinger Bands** and **MACD**  
- **Time series decomposition** and **ACF**  
- **Holt-Winters forecasting**  
- **Anomaly detection** via multiple methods  

## Interactive Dashboard

- Real-time price monitoring  
- Historical price charts with Plotly  
- Technical indicators overlays  
- Forecasting and anomaly highlights  
- CSV download  

## Usage Examples

\`\`\`python
from SecureBitcoin_utils import *

# Fetch & encrypt
key = derive_key("your_password")
price = fetch_bitcoin_price()
encrypted = encrypt_data(price, key)

# Launch dashboard
streamlit run streamlit_app.py
\`\`\`

## Development Guidelines

- Follow **PEP 8** and use type hints  
- **Do not commit** encryption keys  
- Validate inputs and handle errors  

## Contributing

1. Fork the repository  
2. Create a feature branch  
3. Make your changes  
4. Submit a pull request  

## License

MIT License (see \`LICENSE\`)  

## Acknowledgments

CoinGecko API • Streamlit • Docker • DATA605  

## Contact

Open a GitHub issue for questions.
