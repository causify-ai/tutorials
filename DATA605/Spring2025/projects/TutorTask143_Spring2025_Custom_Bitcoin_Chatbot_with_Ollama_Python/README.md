## Custom Bitcoin Chatbot with Ollama Python
# Manoj Kumar Bashaboina, 121333377

## Introduction

Bitcoin Assistant is an advanced Bitcoin currency assistant that provides real-time information, historical analysis, and machine learning-based price predictions for Bitcoin. This project leverages the power of Ollama,  Retrieval-Augmented Generation (RAG) combined with local Large Language Models (LLMs) to deliver accurate, context-aware responses with complete data privacy  

At the core of Bitcoin Assistant  is Ollama, an innovative open-source framework that revolutionizes how we deploy and interact with LLMs. Ollama functions similarly to Docker but for AI models - it packages model weights, configurations, and parameters into a unified, easy-to-deploy format. This approach democratizes access to powerful language models by enabling them to run entirely on local hardware without depending on external cloud services.

The system features a user-friendly Streamlit interface with real-time price tracking, historical data visualization, sentiment analysis of crypto news, technical indicators, and LSTM-based price prediction. By combining these components, BitcoinChat AI delivers a comprehensive cryptocurrency analysis platform that handles natural language queries with remarkable accuracy and speed.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  External APIs  │     │   Data Cache    │     │  LSTM Model     │
│  (CoinGecko,    │────▶│  (Historical &  │────▶│  (Price         │
│   News API,     │     │   Real-time)    │     │   Prediction)   │
│   yFinance)     │     └─────────────────┘     └─────────────────┘
└────────┬────────┘              │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Processing Layer                      │
│   (CryptoData class, Sentiment Analysis, Technical Indicators)  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Knowledge Base / Vector Store               │
│                  (FAISS with Document Embeddings)               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         RAG System                              │
│     (Retrieval, Context Formation, Query Processing)            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Language Model                            │
│              (Ollama running Mistral model)                     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Streamlit UI                               │
│  (User Interface, Visualization, Interactive Components)        │
└─────────────────────────────────────────────────────────────────┘
```


## Technology Overview

### Ollama Framework

Ollama serves as the foundational infrastructure for this project, providing several key capabilities:

- **Local LLM Deployment**: Runs powerful language models like Mistral completely offline on standard hardware
- **Model Management**: Simplifies pulling, running, and managing LLM models through a straightforward CLI
- **API Integration**: Exposes models through a REST API that enables seamless integration with applications
- **Resource Efficiency**: Optimizes memory usage and performance for consumer-grade hardware
- **Model Packaging**: Bundles weights, configurations, and prompt templates in self-contained units


### Ollama Python SDK

The Ollama Python library provides the programmatic interface between our application and the locally running models:

- **Seamless Integration**: Connects Python applications to Ollama's REST API with minimal code
- **Model Interaction**: Facilitates generation, chat, and embedding creation with simple function calls
- **Parameter Control**: Enables fine-tuning of temperature, context length, and other inference parameters
- **Streaming Support**: Allows for real-time streaming of model responses for more responsive UX


### RAG Architecture

The project implements an advanced Retrieval Augmented Generation (RAG) system that:

- **Organizes Knowledge**: Structures cryptocurrency data in vector databases for efficient retrieval
- **Augments Context**: Enriches LLM prompts with relevant, up-to-date cryptocurrency information
- **Improves Accuracy**: Reduces hallucinations by grounding responses in factual, timestamped data
- **Optimizes Relevance**: Uses metadata filtering and multi-query retrieval techniques for better results


### Time Series Forecasting

The integrated LSTM neural network enables:

- **Price Prediction**: Forecasts potential Bitcoin prices up to 30 days in the future
- **Trend Analysis**: Identifies patterns in historical price movements
- **Visualization**: Presents predictions alongside historical data in interactive charts
- **Confidence Metrics**: Provides transparency about prediction certainty and limitations


## Project Capabilities

BitcoinChat AI offers a comprehensive suite of cryptocurrency analysis features:

- **Natural Language Understanding**: Interprets complex queries about cryptocurrency prices, trends, and market conditions
- **Real-time Data Access**: Integrates with CoinGecko API for up-to-date price information and market data
- **Historical Analysis**: Maintains a 15-year record of Bitcoin prices for long-term trend analysis
- **Sentiment Analysis**: Evaluates market sentiment through analysis of recent cryptocurrency news
- **Technical Indicators**: Calculates and interprets RSI, MACD, and Bollinger Bands for technical analysis
- **Future Forecasting**: Predicts potential price movements using LSTM neural networks
- **Date-Based Queries**: Precisely answers questions about prices on specific dates in the past


### Libraries and Frameworks

- **LangChain**: RAG implementation and prompt engineering
- **FAISS**: Vector database for efficient similarity search
- **TensorFlow/Keras**: LSTM neural networks for price prediction
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive data visualization
- **yfinance**: Historical financial data
- **NLTK**: Natural language processing for sentiment analysis


### Data Sources

- **CoinGecko API**: Real-time cryptocurrency prices and market data
- **News API**: Current news articles for sentiment analysis
- **yFinance**: Extended historical data (up to 15 years)


## Setup and Dependencies

### Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- 8GB+ RAM recommended for running the Mistral model


### Docker Setup

1. Clone the repository:

```bash
git clone TutorTask143_Spring2025_Custom_Bitcoin_Chatbot_with_Ollama_Python
cd  TutorTask143_Spring2025_Custom_Bitcoin_Chatbot_with_Ollama_Python
```

2. Create a `.env` file with your configuration:

```
# API Keys
NEWS_API_KEY=your_news_api_key_here
 
```
3. Docker File 

```bash
 
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NLTK data download
RUN python -c "import nltk; nltk.download('vader_lexicon')"

# Copy application code
COPY . .

EXPOSE 8501

# Command to run when container starts
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

```

4. Docker-compose file 

```bash
services:
  crypto_assistant:
    build: .
    ports:
      - "8501:8501"  # Streamlit port
    depends_on:
      - ollama
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - VECTOR_DB_PATH=/app/faiss_index
      - CACHE_DIR=/app/cache
    volumes:
      - ./:/app
      - ./models:/app/models 
    env_file:
    - .env 
    command: [
      "sh",
      "-c",
      "find /usr/local/lib/python3.10/site-packages/langchain -type f -name '*.py' -exec sed -i 's|http://localhost:11434|http://ollama:11434|g' {} \\; &&
      find /app -type f -name '*.py' -exec sed -i 's|http://localhost:11434|http://ollama:11434|g' {} \\; &&
      echo 'Waiting for Ollama to initialize...' &&
      sleep 30 &&
      python -c \"import requests; requests.post('http://ollama:11434/api/pull', json={'name': 'nomic-embed-text'})\" &&
      python -c \"import requests; requests.post('http://ollama:11434/api/pull', json={'name': 'mistral'})\" &&
      streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0"
    ]
    networks:
      - crypto_network

  ollama:
    image: ollama/ollama
    volumes:
      - ollama_models:/root/.ollama
    ports:
      - "11434:11434"
    command: serve
    networks:
      - crypto_network

networks:
  crypto_network:
    driver: bridge

volumes:
  ollama_models:
```

5. Build and run with Docker Compose:

```bash
docker compose up --build
```
6. Open this url 
```bash 
http://localhost:8501/
```

### Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the Ollama server:

```bash
ollama serve
```

3. In another terminal, pull the required models:

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

4. Launch the Streamlit application:

```bash
streamlit run streamlit_app.py 
```


## Environment Setup

The application uses environment variables for configuration, which can be set in your `.env` file or directly in the Docker Compose configuration:

- **API Keys**: For accessing CoinGecko and News API
- **Model Configuration**: Settings for the Ollama/Mistral model
- **Data Paths**: Vector store and cache locations
- **Update Intervals**: How frequently to refresh data
- **Rate Limits**: To respect API rate limitations

For Docker deployments, these settings are injected into the container through the environment section in `docker-compose.yml`.

## Usage

### Accessing the Application

Once running, access the BitcoinChat AI interface at:

- **Docker**: http://localhost:8501
- **Local**: http://localhost:8501


### Core Features

- **Chat Interface**: Ask natural language questions about Bitcoin and cryptocurrencies
- **Current Price Display**: Real-time price information with 24-hour change
- **Market Summary**: Overview of cryptocurrency market conditions
- **Sentiment Analysis**: Analysis of current market sentiment based on news
- **Price Prediction**: ML-based forecast of future Bitcoin prices
- **Date-Based Queries**: Historical price lookup for specific dates
- **Technical Analysis**: Indicators like RSI, MACD, and Bollinger Bands


### Sample Queries

- "What is the current Bitcoin price?"
- "What was the price of Bitcoin on May 10, 2025?"
- "How has Bitcoin performed over the last 7 days?"
- "What's the market sentiment right now?"
- "Predict Bitcoin price 14 days ahead"
- "What are the technical indicators for Bitcoin?"


## Data Collection APIs

### CoinGecko API

- **Purpose**: Real-time cryptocurrency data and market information
- **Endpoints Used**:
    - `/simple/price`: Current prices, market cap, and 24h change
    - `/coins/{id}`: Detailed market data for specific cryptocurrencies
    - `/coins/{id}/market_chart`: Historical price data


### News API

- **Purpose**: Gathering news articles for sentiment analysis
- **Endpoints Used**:
    - `/everything`: News articles related to cryptocurrencies


### yFinance API

- **Purpose**: Extended historical data (up to 15 years)
- **Usage**: Fallback for historical analysis when CoinGecko data is limited




### Flow Description

1. **Data Collection**: External APIs provide cryptocurrency data and news
2. **Data Processing**: Information is processed, analyzed, and structured
3. **Knowledge Base**: Processed data is stored in a vector database
4. **RAG System**: User queries are analyzed and relevant information is retrieved
5. **Language Model**: Mistral model generates human-like responses based on context
6. **User Interface**: Streamlit presents the information with interactive components

## Results and Performance

### Response Time

- **Standard Queries**: 1-3 seconds
- **Complex Analysis**: 2 - 3 minutes
- **Price Predictions**: 5-10 seconds (includes LSTM model inference)


### Accuracy

- **Price Data**: Real-time (within 5 minutes) from CoinGecko API
- **Historical Data**: High accuracy with 15 years of historical context
- **Sentiment Analysis**: Based on analysis of recent cryptocurrency news
- **Price Predictions**: LSTM model trained on historical data with validation


### Memory Usage

- **Docker Container**: 2-4GB RAM depending on query complexity
- **Vector Store Size**: ~100MB for Bitcoin and Ethereum data
- **Model Size**: ~4GB for Mistral model

By combining real-time data, historical analysis, and machine learning predictions, BitcoinChat AI delivers comprehensive cryptocurrency insights through a user-friendly interface, making complex market information accessible and actionable.

<div style="text-align: center">⁂</div>

[^1]: api.py

[^2]: bitcoinchatbot.py

[^3]: data_processor.py

[^4]: docker_build.log

[^5]: docker-compose.yml

[^6]: price_predictor.py

[^7]: streamlit_app.py

[^8]: utils.py

[^9]: vector_store.py

[^10]: https://github.com/public-apis/public-apis/blob/master/README.md

[^11]: https://github.com/docker/mcp-servers

[^12]: https://www.docker.com/blog/readmeai-an-ai-powered-readme-generator-for-developers/

[^13]: https://www.leewayhertz.com/how-to-build-an-ai-app/

[^14]: https://stackoverflow.com/questions/50238621/how-to-set-environment-variable-into-docker-container-using-docker-compose

[^15]: https://easypanel.io/templates

[^16]: https://docs.docker.com/compose/releases/release-notes/

[^17]: https://wickrinc.github.io/wickrio-docs/

[^18]: https://www.projectpro.io/article/mlops-projects-ideas/486

[^19]: https://marketplace.fedramp.gov

