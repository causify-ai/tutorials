# Bitcoin News Keyword Trend Analysis

This project analyzes Bitcoin-related news articles to identify trending keywords and correlate their frequency with Bitcoin price movements over time.

## Features

- Fetches Bitcoin-related news articles using NewsAPI
- Extracts keywords using TextBlob's NLP capabilities
- Integrates historical Bitcoin price data
- Performs trend correlation analysis
- Visualizes keyword trends against price movements
- Implements Granger causality tests

## Setup

### Option 1: Regular Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your API keys:
   ```
   NEWSAPI_KEY=your_news_api_key
   ```

### Option 2: Docker Setup

1. Clone this repository
2. Create a `.env` file with your API keys as shown above
3. Build the Docker image:
   ```bash
   docker build -t bitcoin-news-analysis .
   ```
4. Run the container:
   ```bash
   docker run --env-file .env bitcoin-news-analysis
   ```

## Security Notes for GitHub

When committing this project to GitHub:

1. **Never commit your .env file** - It's already in .gitignore to prevent accidental commits
2. Use the provided `.env.example` as a template
3. For production deployments, consider using more secure methods for managing secrets:
   - GitHub Secrets for GitHub Actions
   - Environment variables in your CI/CD pipeline
   - Secret management services like AWS Secrets Manager, HashiCorp Vault, etc.

## Project Structure

- `main.py`: Main script to run the analysis
- `fetch_news.py`: News API integration
- `fetch_prices.py`: Bitcoin price data fetching
- `extract_keywords.py`: TextBlob keyword extraction
- `analyze_trends.py`: Trend analysis and correlation
- `visualize.py`: Data visualization
- `granger.py`: Granger causality tests

## Usage

### Running without Docker

Run the main script:
```bash
python main.py
```

### Running with Docker

After building the image:
```bash
docker run --env-file .env bitcoin-news-analysis
```

To see visualizations, you can mount a volume for the figures:
```bash
docker run --env-file .env -v $(pwd)/figures:/app/figures bitcoin-news-analysis
```

## Dependencies

- textblob: NLP tasks
- newsapi-python: News article fetching
- pandas: Data manipulation
- statsmodels: Statistical analysis
- plotly: Interactive visualizations

## License

MIT License 