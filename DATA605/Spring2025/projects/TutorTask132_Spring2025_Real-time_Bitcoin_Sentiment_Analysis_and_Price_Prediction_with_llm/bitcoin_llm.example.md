# bitcoin_llm: Bitcoin Sentiment Dashboard

## Overview

This dashboard visualizes Bitcoin-related sentiment extracted using LLMs and predicts price using Prophet/LSTM.

## Components

- `Streamlit` dashboard in `app.py`
- Realtime sentiment fetched from NewsAPI
- Sentiment analysis using OpenAI's GPT
- Time series modeling using Prophet or LSTM

## Usage

```bash
docker build -t bitcoin-llm .
docker run -p 8501:8501 --env-file .env bitcoin-llm
