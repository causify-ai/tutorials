 # Bitcoin RAG Assistant

A powerful bitcoincurrency information system combining real-time data retrieval with local LLM-powered Retrieval Augmented Generation (RAG) using Ollama.

## Overview

The Bitcoin RAG Assistant is an advanced tool designed to provide real-time cryptocurrency insights, analysis, and information through a conversational interface. The system aggregates data from various sources including price information, historical trends, detailed market data, and recent news, storing it in a vector database for efficient retrieval and analysis.

## Key Features

- **Real-time Bitcoincurrency Data**: Fetches current prices, market statistics, and detailed information from CoinGecko API
- **Historical Analysis**: Processes and analyzes 365 days of historical data with various timeframes (7, 30, 90 days)
- **News Integration**: Retrieves and processes recent Bitcoincurrency news articles
- **Local LLM Integration**: Utilizes Ollama models for private, offline question answering
- **Vector Database**: Stores processed data in FAISS for efficient semantic search
- **Scheduled Updates**: Automatically refreshes data at configurable intervals
- **Multiple Interfaces**: Command-line chat interface and web application with Flask

## Architecture

The system consists of several core components:

1. **BitcoinData**: Fetches, processes, and formats Bitcoincurrency data from various sources
2. **RAGSystem**: Manages the vector database and question-answering capability
3. **BitcoinAssistant**: Orchestrates the entire system, providing a high-level interface
4. **User Interfaces**: Both console and web interfaces for user interaction

## Requirements

- Python 3.10.16
- requests==2.31.0
- pandas==2.1.0
- numpy==1.24.4
- langchain==0.0.310
- faiss-cpu==1.7.4
- ollama==0.1.5
- schedule==1.2.0
- flask==2.3.3
- Ollama installed and running locally
- Internet connection for data retrieval
- News API key

## Installation

1. Clone the repository:
   ```bash
    
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Ollama is installed and running:
   ```bash
   # Check Ollama installation instructions at https://ollama.ai
   # Start the Ollama service
   ollama serve
   ```

4. Pull required models:
   ```bash
   ollama pull llama3  # or your preferred LLM model
   ollama pull nomic-embed-text  # for embeddings
   ```

5. Configure your News API key:
   - Sign up at https://newsapi.org to get an API key
   - Replace `NEWS_API_KEY` in the code with your API key

## Configuration

Several key parameters can be configured in the code:

- `OLLAMA_MODEL`: LLM model to use (default: "llama3")
- `UPDATE_INTERVAL`: How often to update data in minutes (default: 15)
- `COINGECKO_RATE_LIMIT_WAIT`: Time to wait between CoinGecko API calls (default: 6 seconds)
- `VECTOR_DB_PATH`: Location to store the FAISS vector database (default: "faiss_index")

## Usage

### Command Line Interface

Run the assistant in command-line mode:

```bash
python bitcoinassistant.py
```

Command line options:
- Type questions to interact with the assistant
- Type `update` to force a data update
- Type `exit` to quit

### Web Interface

Run the assistant as a web application:

```bash
python bitcoinassistant.py --web --port 5000
```

Command line arguments:
- `--web`: Run as a web application
- `--port`: Port for web server (default: 5000)
- `--debug`: Run in Flask debug mode
- `--update`: Force data update on startup

Then access the web interface at `http://localhost:5000`

## Example Queries

The system can answer a wide range of Bitcoincurrency-related questions:

- "What is the current price of Bitcoin?"
- "How has Ethereum performed over the last 30 days?"
- "What's the market cap ranking of bitcoin?"
- "What are the recent news for Bitcoin?"
- "What's the yearly trend for Bitcoin?"
- "Compare Bitcoin performance this quarter"
- "What's the most volatile Bitcoincurrency in the last week?"
- "Is Bitcoin in an uptrend or downtrend right now?"

## Data Sources

- Price and market data: CoinGecko API
- News articles: NewsAPI

## Project Structure

```
TutorTask143_Spring2025_Custom_Bitcoin_Chatbot_with_Ollama_Python /
├── bitcoinassistant.py        # Main application file
├── requirements.txt     # Dependencies
├── templates/           # Web interface templates
│   └── index.html       # Main web interface
├── faiss_index/         # Vector database storage (created at runtime)
└── crypto_rag.log       # Log file (created at runtime)
```

## Dependencies

- langchain: For RAG components
- FAISS: Vector database
- Ollama: Local LLM integration
- pandas & numpy: Data processing
- Flask: Web interface
- requests: API calls
- schedule: Scheduled updates

## Limitations

- Rate limited by CoinGecko's free API tier
- Quality of answers depends on the Ollama model used
- Historical data limited to 1 year
- Limited cryptocurrency coverage (configurable)

## Future Enhancements

- Support for more cryptocurrencies
- Technical analysis indicators
- Portfolio tracking capabilities
- Multi-source data aggregation
- Improved visualization in web interface
- Support for additional LLM backends

## License

[MIT License](LICENSE)

## Acknowledgements

- CoinGecko for bitcoincurrency data API
- NewsAPI for news retrieval
- Ollama for local LLM capabilities
- LangChain for RAG framework