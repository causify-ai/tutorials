#!/bin/bash
echo "🚀 Running 'streamlit-bitcoin-tracker' container on port 8501..."
docker run -p 8501:8501 --name streamlit-bitcoin-tracker-container streamlit-bitcoin-tracker
