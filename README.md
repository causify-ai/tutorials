# tutorials
Real-Time Bitcoin Price Analysis with FastAPI

📌 Project Overview
This project is a real-time cryptocurrency monitoring and analysis dashboard built using FastAPI, a high-performance web framework for building APIs with Python. It fetches real-time Bitcoin prices using the CoinGecko API, stores them in a lightweight SQLite database, and provides interactive visualizations using Plotly.

🔧 Key Features
📥 Real-Time Price Fetching: Live BTC/USD price from CoinGecko on each page load

💾 Historical Price Storage: Data stored in SQLite for trend analysis

📈 Interactive Dashboard: Shows latest prices, moving averages, and volatility plots

🧠 Anomaly Detection: Optional support to detect local peaks and valleys

🐳 Dockerized Deployment: One-step reproducible container setup


⚙️ Technologies Used
Tool	Purpose
FastAPI	Backend API framework
SQLite	Lightweight database to store price logs
Pandas	Data manipulation and time-series analysis
Plotly	Interactive plots and dashboard UI
Uvicorn	ASGI server for running FastAPI
Docker	Containerization of the full app

🗂️ Project Structure
bash
Copy
Edit
TutorTask179_Spring2025_Real_Time_Bitcoin_Price_Analysis_with_FastAPI/
├── app/
│   └── main.py                # FastAPI application logic
├── bitcoin_5yr_history.csv    # Year-long historical data from CoinGecko
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker build instructions
├── README.md                  # Project documentation
├── XYZ.API.ipynb              # Clean notebook for API usage testing
├── XYZ.example.ipynb          # End-to-end example with plots & insights
└── XYZ_utils.py               # Utility functions (future extension)


Project Execution Flow
🔁 1. Clone the GitHub Repo
bash
Copy
Edit
git clone --recursive https://github.com/yourusername/tutorials.git
cd tutorials/DATA605/Spring2025/projects/TutorTask179_Spring2025_Real_Time_Bitcoin_Price_Analysis_with_FastAPI
🐳 2. Docker Build
bash
Copy
Edit
docker build -t bitcoin-dashboard .
🧱 3. Docker Run
bash
Copy
Edit
docker run -d -p 8000:8000 --name bitcoin-dashboard-container bitcoin-dashboard
🌐 4. Access FastAPI App
Open your browser and visit:

bash
Copy
Edit
http://localhost:8000/dashboard
📊 Dashboard Features
Live Price: Shows most recent BTC price fetched on load

Plot 1: Yearly BTC trend with 30-day moving average

Plot 2: Separate moving average visualization

Plot 3 (Optional): Anomaly detection using local minima/maxima

📁 Outputs
bitcoin_5yr_history.csv: Daily prices stored locally and read by the app

SQLite database (prices.db) for real-time inserted values

Plots rendered via /dashboard route

Use Bollinger Bands or MACD for trend detection

Integrate Plotly Dash for advanced front-end UI

👨‍💻 Author
Manish Cheeti

UID: 121329745

Spring 2025 — DATA605 PCS1

University of Maryland, College Park
