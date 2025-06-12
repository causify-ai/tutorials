#!/bin/bash
echo "🔁 Building and launching Docker container..."
docker stop streamlit-bitcoin-tracker-container 2>/dev/null
docker rm streamlit-bitcoin-tracker-container 2>/dev/null
docker build -t streamlit-bitcoin-tracker .
docker run -p 8501:8501 --name streamlit-bitcoin-tracker-container streamlit-bitcoin-tracker
