# Bitcoin News Sentiment Analysis

This project fetches recent Bitcoin (and other cryptocurrency) news articles, analyzes their sentiment using a Language Model (LLM) via LiteLLM, and provides tools to visualize and save the results. It includes functionality for caching results, multiple LLM provider support, and offers interfaces via Jupyter Notebooks and a command-line script.

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Architecture](#architecture)
3.  [Features](#features)
4.  [File Structure](#file-structure)
5.  [Requirements](#requirements)
6.  [Setup](#setup)
    * [Docker Setup](#docker-setup)
    * [API Keys](#api-keys)
    * [LLM Provider Prerequisites](#llm-provider-prerequisites)
    * [Using Ollama (Local LLM)](#using-ollama-local-llm)
7.  [How to Run](#how-to-run)
    * [Using Docker](#using-docker)
    * [Using Jupyter Notebooks](#using-jupyter-notebooks)
    * [Using the Python Script](#using-the-python-script)
8.  [Configuration Details](#configuration-details)
9.  [Output](#output)
10. [Examples and Use Cases](#examples-and-use-cases)
11. [API Reference](#api-reference)

## Project Overview

The core functionality involves:
1.  **Fetch**: Retrieve cryptocurrency-related news articles from NewsAPI within a specified date range.
2.  **Score**: Analyze the sentiment of each article (Positive, Neutral, Negative) using an LLM via LiteLLM.
3.  **Aggregate**: Collect results, cache analyzed articles, and save them to a CSV file.

The system is designed to be modular, allowing for easy customization of the target cryptocurrency, LLM provider, and analysis parameters. Caching is implemented to optimize API token usage and prevent redundant processing.

## Architecture

The system is built around a central utility module (`bitcoin_utils.py`) that handles configuration, news fetching, text processing, sentiment analysis via LLM, and caching. This module is then utilized by:
* A command-line script (`bitcoin_news_sentiment.py`) for automated and scheduled analyses.
* Jupyter Notebooks (`bitcoin_news_sentiment.ipynb`, `bitcoin.API.ipynb`, `bitcoin.example.ipynb`) for interactive exploration, demonstrations, and examples.

## Features
* **Multi-Cryptocurrency Support**: While focused on Bitcoin, adaptable for news sentiment analysis of other cryptocurrencies.
* **Flexible News Fetching**: Retrieves news articles using NewsAPI with customizable date ranges and query terms.
* **Advanced Sentiment Analysis**: Utilizes LLMs via LiteLLM for nuanced sentiment classification (Positive, Neutral, Negative).
* **Provider Choice**: Supports multiple LLM providers (Together AI, OpenAI, HuggingFace, Gemini, Ollama).
* **Cost-Efficient Caching**: Caches analyzed articles to minimize redundant API calls and reduce processing time.
* **User-Friendly Configuration**: Manages API keys and model preferences through a `.env` file and a central `Config` class.
* **Versatile Interfaces**:
    * Interactive Jupyter Notebooks for exploration, demonstration, and detailed examples.
    * Robust command-line script for automated batch processing and scheduled tasks.
* **Structured Data Output**: Saves analysis results in CSV format for easy access and further analysis.
* **Insightful Visualizations**: Generates pie charts and time-series plots to represent sentiment distributions and trends.
* **Scheduled Analysis**: The CLI script can be configured for continuous, scheduled sentiment monitoring.

## File Structure
* `.env` (to be created by user): Stores API keys and sensitive configuration.
* `bitcoin_utils.py`: The core Python module containing all utility functions for configuration, news fetching, sentiment analysis, caching, and visualization helpers.
* `bitcoin_news_sentiment.py`: The main command-line Python script for running the full sentiment analysis pipeline. It supports various arguments for customization and scheduled execution.
* `bitcoin_news_sentiment.ipynb`: A Jupyter Notebook providing a step-by-step demonstration of the basic Bitcoin news sentiment analysis workflow.
* `bitcoin.API.ipynb`: A Jupyter Notebook that demonstrates how to use the functions in `bitcoin_utils.py` programmatically, showcasing its API-like capabilities.
* `bitcoin.example.ipynb`: An advanced Jupyter Notebook that offers end-to-end examples, including using different LLM providers, visualizing sentiment trends over time, and customizing the analysis for various cryptocurrencies.
* `bitcoin_API.md`: A Markdown document providing a detailed reference for the functions and classes within `bitcoin_utils.py`. It includes an architecture diagram of the utilities, function signatures, parameter explanations, and setup details specific to the utilities.
* `bitcoin.example.md`: A Markdown document that outlines practical, real-world applications and use cases. This includes instructions for scheduling sentiment logging, examples of visualizing the output data using Dash and Matplotlib, and tips for customizing the analysis.
* `data/` (directory, created automatically):
    * `article_cache.json`: Stores cached news articles and their sentiment scores to avoid re-processing.
    * `bitcoin_sentiment_results.csv` (or `[crypto]_sentiment_results.csv`): The output CSV file containing the analyzed news data.
* `exports/` (directory, created by example scripts in `bitcoin.example.md`): Intended to store data exported in alternative formats like Excel or JSON.
* `requirements.txt`: Python package dependencies.
* `docker_data605_style/`: Docker configuration directory
  * `Dockerfile`: Container configuration
  * `docker-compose.yml`: Multi-container setup
  * `run_jupyter.sh`: Script to start Jupyter notebook

## Requirements

* Python 3.11 or higher
* Docker and Docker Compose (for containerized setup)
* Required Python packages (specified in requirements.txt):
    * `litellm>=1.69.2`
    * `requests>=2.32.3`
    * `python-dotenv>=1.1.0`
    * `pandas>=2.2.3`
    * `tiktoken>=0.9.0`
    * `ipywidgets>=8.1.7`
    * `plotly>=6.1.0`
    * `matplotlib>=3.10.0`
    * `schedule>=1.2.2`
    * `jupyterlab` and `notebook`
    * Additional dependencies as listed in requirements.txt

You can install these using pip:
```bash
pip install -r requirements.txt
```

## Setup

### Docker Setup

The project includes a Docker configuration for easy setup and consistent environment. To get started:

1. Make sure you have Docker and Docker Compose installed on your system.

2. Navigate to the Docker configuration directory:
```bash
cd docker_data605_style
```

3. Run the startup script:
```bash
./run_jupyter.sh
```

This script will:
- Create necessary directories
- Set up proper permissions
- Build and start the Docker containers
- Start Jupyter Notebook and Ollama services

4. Access Jupyter Notebook:
- Open your web browser and navigate to: `http://localhost:8888`
- The Jupyter interface will be available without a password

### Running the Script in Docker

After starting the Docker containers, you can run the Bitcoin news sentiment analysis script in two ways:

1. **Through Jupyter Notebook**:
   - Open `bitcoin_news_sentiment.ipynb` in Jupyter
   - Run the cells sequentially to execute the analysis

2. **Through Terminal**:
   - Open a new terminal
   - Connect to the running container:
   ```bash
   docker exec -it data605_app_1 bash
   ```
   - Run the script:
   ```bash
   python bitcoin_news_sentiment.py
   ```

   Additional command-line options:
   ```bash
   # Analyze news from the last 5 days
   python bitcoin_news_sentiment.py --days 5

   # Use Ollama as the LLM provider
   python bitcoin_news_sentiment.py --provider ollama

   # Run continuous analysis every 30 minutes
   python bitcoin_news_sentiment.py --loop --interval 30
   ```

### Data Storage

- All analysis results are saved in the `data/` directory
- The directory is automatically created and mounted in the container
- Results are persisted between container restarts

### Stopping Docker Containers

To stop the containers:
```bash
cd docker_data605_style
docker-compose down
```

To stop and remove all data (including volumes):
```bash
cd docker_data605_style
docker-compose down -v
```

### Manual Setup

If you prefer to run the project without Docker:

1. Clone the repository or download the project files.
2. Create and activate a Python virtual environment (recommended).
3. Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### API Keys
Populate the `.env` file with your API credentials:

```env
# Mandatory for fetching news
NEWS_API_KEY="YOUR_NEWS_API_KEY"

# Required if using the respective LLM provider
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
TOGETHER_API_KEY="YOUR_TOGETHER_API_KEY"
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
HUGGINGFACE_API_KEY="YOUR_HUGGINGFACE_API_KEY"
```

### LLM Provider Prerequisites

| Provider      | API Key Required | Setup Notes                     |
|---------------|------------------|---------------------------------|
| OpenAI        | Yes              | Account with API access.        |
| Together AI   | Yes              | Account with API access.        |
| Google Gemini | Yes              | Google AI Studio API key.       |
| HuggingFace   | Yes              | HuggingFace API token.          |
| Ollama        | No               | Local Ollama server must be running. |

### Using Ollama (Local LLM)

If you wish to use a locally run LLM via Ollama (which doesn't require an external API key):

1.  **Install Ollama:** Download and install Ollama from [ollama.com/download](https://ollama.com/download).
2.  **Start the Ollama Server:** Open your terminal and execute `ollama serve`. By default, it runs on `localhost:11434`.
3.  **(Optional) Pull a Model:** To use a specific model (e.g., Llama 2), run `ollama pull llama2` in the terminal. A list of available models can be found at [ollama.com/library](https://ollama.com/library).

When running the analysis script or notebook, ensure you select `ollama` as the provider.

## How to Run

### Using Docker

After starting the Docker containers, you can run the Bitcoin news sentiment analysis script in two ways:

1. **Through Jupyter Notebook**:
   - Open `bitcoin_news_sentiment.ipynb` in Jupyter
   - Run the cells sequentially to execute the analysis

2. **Through Terminal**:
   - Open a new terminal
   - Connect to the running container:
   ```bash
   docker exec -it data605_app_1 bash
   ```
   - Run the script:
   ```bash
   python bitcoin_news_sentiment.py
   ```

   Additional command-line options:
   ```bash
   # Analyze news from the last 5 days
   python bitcoin_news_sentiment.py --days 5

   # Use Ollama as the LLM provider
   python bitcoin_news_sentiment.py --provider ollama

   # Run continuous analysis every 30 minutes
   python bitcoin_news_sentiment.py --loop --interval 30
   ```

### Using Jupyter Notebooks

* **`bitcoin_news_sentiment.ipynb`**:
    * Ideal for a first look at the project's capabilities.
    * Run cells sequentially to fetch news, analyze sentiment, and view results in a table.
* **`bitcoin.API.ipynb`**:
    * Demonstrates programmatic use of the functions within `bitcoin_utils.py`.
    * Useful for understanding how to integrate the utilities into other Python projects.
* **`bitcoin.example.ipynb`**:
    * Provides comprehensive, real-world usage examples.
    * Shows how to analyze sentiment for different cryptocurrencies, generate various visualizations (pie charts, time series, rolling averages), and explore data.

To use the notebooks:

1.  Ensure Jupyter Notebook or JupyterLab is installed.
2.  Navigate to the project directory and launch Jupyter.
3.  Open the desired `.ipynb` file and execute the cells.

### Command-Line Script (`bitcoin_news_sentiment.py`)

The `bitcoin_news_sentiment.py` script allows for running the sentiment analysis pipeline from the terminal.

**Basic Execution:**
```bash
python bitcoin_news_sentiment.py
```

This command will fetch Bitcoin news for the past day using the default LLM provider and save the results.

**Available Arguments:**

* `--days DAYS`: Specify the number of past days to fetch news from (default: 1).
* `--week`: A shortcut to fetch news from the last 7 days (overrides `--days`).
* `--from-date YYYY-MM-DD`: Define a specific start date for fetching articles.
* `--to-date YYYY-MM-DD`: Define a specific end date for fetching articles.
* `--page-size PAGE_SIZE`: Set the number of articles to retrieve per request (default: 10; NewsAPI free tier limit is 100).
* `--provider PROVIDER_NAME`: Choose the LLM provider (e.g., openai, together_ai, huggingface, gemini, ollama).
* `--loop`: Enable continuous analysis, running at scheduled intervals.
* `--interval MINUTES`: Set the interval in minutes for the `--loop` mode (default: 60).

**Example Commands:**

Analyze news from the last 5 days for Bitcoin, fetching 25 articles, using OpenAI:
```bash
python bitcoin_news_sentiment.py --days 5 --page-size 25 --provider openai
```

Run analysis continuously every 30 minutes using a local Ollama instance:
```bash
python bitcoin_news_sentiment.py --provider ollama --loop --interval 30
```

*(Note: For analyzing cryptocurrencies other than Bitcoin via the script, you might need to directly modify the default query term in the `Workspace_bitcoin_news` function within `bitcoin_utils.py`, or extend the script to accept a query argument. The notebooks provide clearer examples of this customization.)*

## Settings and Configuration

Key settings for the project are managed through the `Config` class in `bitcoin_utils.py` and can be influenced by environment variables in the `.env` file.

* **API Keys**: As detailed in the Setup section, these are loaded from `.env`. `NEWS_API_KEY` is mandatory.
* **LLM Provider (`PROVIDER`)**:
    * The default provider is `together_ai` (defined in `Config` class).
    * This can be changed directly in the `Config` class for a project-wide default.
    * It can be overridden in Jupyter Notebooks by setting the `PROVIDER` variable.
    * It can be specified for the script using the `--provider` command-line argument.
* **LLM Model ID (`MODEL_ID`)**:
    * The default model is `mistralai/Mixtral-8x7B-Instruct-v0.1` (for `together_ai`).
    * Provider-specific model IDs are listed in `Config.provider_configs` within `bitcoin_utils.py`. These can be adjusted if you prefer a different model compatible with LiteLLM and your chosen provider.
* **Maximum Tokens (`MAX_TOKENS`)**:
    * The maximum number of tokens from an article's content to send to the LLM for analysis (default: `10000`, defined in `Config`). Helps manage API costs and context window limits. Text is truncated if it exceeds this.
* **Prompt Template (`PROMPT_TEMPLATE`)**:
    * The template for the prompt sent to the LLM for sentiment classification is defined in the `Config` class. This can be modified to change how the LLM is instructed to perform the analysis (e.g., different sentiment categories, more detailed instructions).
* **Data Directories**:
    * `DATA_DIR`: Path to the directory where data files are stored (default: `./data/`, created if it doesn't exist).
    * `CSV_PATH`: Path to the output CSV file for sentiment results (default: `DATA_DIR / "bitcoin_news_sentiment.csv"`).
    * `CACHE_PATH`: Path to the JSON file used for caching article analysis (default: `DATA_DIR / "article_cache.json"`).

These settings provide a centralized way to control the behavior of the news fetching, analysis, and data storage aspects of the project.

## Output

The project generates several types of output:

* **Console Logs**: During execution, both the script and notebooks print status messages to the console. This includes information on articles being fetched, which articles are processed from cache versus new analyses, the raw sentiment returned by the LLM, and any errors encountered.
* **CSV File (`bitcoin_sentiment_results.csv` or `[crypto]_sentiment_results.csv`)**:
    * This is the primary structured output, saved in the `data/` directory.
    * Columns typically include: `publishedAt`, `headline`, `sentiment` (e.g., Pos, Neg, Ne), `score` (numerical representation of sentiment, e.g., 1, -1, 0), `url` (link to the article), `cost` (estimated cost of LLM API call, if applicable), and `cached` (boolean indicating if the result was from the cache).
* **Cache File (`article_cache.json`)**:
    * A JSON file stored in the `data/` directory.
    * It contains a hash of article content mapped to its analyzed sentiment and score, along with a timestamp. This enables efficient re-use of previous analyses.
* **Visualizations (in Jupyter Notebooks)**:
    * The notebooks (`bitcoin_news_sentiment.ipynb`, `bitcoin.example.ipynb`) generate various plots using Plotly and Matplotlib.
    * These include pie charts of sentiment distribution, time-series line plots of sentiment trends, and rolling average sentiment scores.
* **Exported Files (from `bitcoin.example.md` examples)**:
    * The example scripts in `bitcoin.example.md` demonstrate how to export the processed DataFrame to other formats like Excel (`.xlsx`) or JSON (`.json`), typically saved in an `exports/` directory.
    * It also shows an example of exporting summary statistics in JSON format.

## Examples and Use Cases (`bitcoin.example.md`)

The `bitcoin.example.md` file, along with its corresponding `bitcoin.example.ipynb` notebook, serves as a comprehensive guide to practical applications of this sentiment analysis tool. Key areas covered include:

* **Scheduling Automated Analysis**:
    * Instructions for setting up the `bitcoin_news_sentiment.py` script to run at regular intervals (e.g., hourly) using the `schedule` library.
    * Guidance on deploying the script as a system service (e.g., using `systemd` on Linux) for robust, continuous monitoring.
* **Visualizing Sentiment Data**:
    * Code examples for creating a simple, interactive web dashboard using Plotly Dash to display sentiment trends and distributions from the output CSV.
    * Examples of generating static visualizations (line plots, pie charts) using Matplotlib for quick insights or reports.
* **Customization Techniques**:
    * **Date Range**: How to modify parameters to fetch news from specific historical date ranges or for varying look-back periods (e.g., last 7 days, last 30 days).
    * **LLM Providers**: Step-by-step on how to switch between different supported LLM providers (OpenAI, Together.ai, Ollama, Gemini) by changing the configuration.
    * **Prompt Engineering**: Tips on modifying the `PROMPT_TEMPLATE` in the `Config` class to tailor the sentiment analysis (e.g., for more granular sentiment categories like 'Very Positive').
* **Data Export**: How to export the analyzed data (Pandas DataFrame) into other common formats such as Excel (`.xlsx`) or JSON, facilitating integration with other tools or workflows.
* **Analyzing Other Cryptocurrencies**: Demonstrates how to adapt the news fetching query to analyze sentiment for cryptocurrencies other than Bitcoin (e.g., Ethereum).

These examples provide actionable guidance for leveraging the tool's full potential in various scenarios, from automated data pipelines to ad-hoc analytical explorations.

## API Reference (`bitcoin_API.md`)

The `bitcoin_API.md` document provides an in-depth reference for the core components and functions found within the `bitcoin_utils.py` module. It is intended for developers who wish to understand the internal workings or extend the project's capabilities. Key sections include:

* **Overview**: A summary of the utility module's role in the sentiment analysis workflow.
* **Architecture Diagram**: A visual representation of the components within `bitcoin_utils.py` and their interactions.
* **Function and Class Reference**:
    * **`Config` Class**: Detailed explanation of the configuration dataclass, its attributes (API keys, provider settings, paths, prompt template), and methods like `load()` for loading from `.env` and the `provider_configs` property.
    * **`Workspace_bitcoin_news()`**: Signature, parameters (`config`, `page_size`, date ranges), return value (list of article dictionaries), and design notes.
    * **`classify_sentiment()`**: Signature, parameters (`text`, `config`), return value (sentiment string, cost), and notes on text truncation and error handling.
    * **Text Processing Functions**: `count_tokens()` and `truncate_text()`, explaining their roles in managing LLM input.
    * **`process_news_articles()`**: The main pipeline function, detailing its parameters, the structure of the returned Pandas DataFrame, and its caching logic.
    * **Visualization Helpers**: `