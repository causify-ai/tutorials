# Bitcoin Price Forecasting System Architecture

This document provides a detailed overview of the system architecture, file structure, and component interactions.

## System Components

The Bitcoin Price Forecasting System consists of three primary components:

1. **Streamlit Web Application**: The main user interface for visualizing Bitcoin price forecasts, technical indicators, and sentiment analysis
2. **Sentiment Analysis Service**: Background service that collects and analyzes Bitcoin news sentiment
3. **PostgreSQL Database**: Stores historical price data, news articles, and sentiment analysis results

## File Structure and Functionality

### Core Application Files

- **app.py**
  - Main Streamlit application entry point
  - Handles user interface, data loading, model configuration, and visualization
  - Integrates all components (forecasting models, technical analysis, sentiment analysis)

- **bitcoin_sentiment.py**
  - Direct Bitcoin sentiment analysis without database dependencies
  - Collects Bitcoin news articles from NewsAPI
  - Analyzes sentiment using TextBlob
  - Returns sentiment summary and data frames

- **sentiment_analysis_helper.py**
  - Simplified interface for sentiment analysis
  - Used for updating sentiment displays in the Streamlit app
  - Provides top Bitcoin sentiment analysis

- **sentiment_dashboard.py**
  - Comprehensive sentiment analysis dashboard
  - Visualizes both hourly and daily sentiment data
  - Shows insights on how sentiment influences price forecasting

- **sentiment_scheduler.py**
  - Manages scheduled sentiment analysis tasks
  - Provides access to collected sentiment data at different frequencies
  - Formats sentiment data for integration with forecasting models

- **sentiment_visualization.py**
  - Visualization tools for sentiment data
  - Includes sentiment trends, distributions, and news samples
  - Calculates correlation between sentiment and price movement

- **scheduled_sentiment_analysis.py**
  - Handles both hourly and daily scheduled sentiment analysis
  - Collects sentiment data at different frequencies
  - Stores data for use by forecasting models

### Source Code Modules (`src/` directory)

- **src/data_collector.py**
  - Fetches Bitcoin price data from various sources (YFinance, CoinGecko)
  - Handles data preprocessing and cleaning
  - Provides real-time price updates

- **src/model.py**
  - Implements Bitcoin price forecasting models
  - Supports ARIMA/SARIMAX for time series analysis
  - Includes model evaluation metrics

- **src/lstm_model.py**
  - LSTM neural network implementation for Bitcoin forecasting
  - Handles data preprocessing specific to LSTM models
  - Provides model training and prediction functions

- **src/transformer_model.py**
  - Transformer-based model for Bitcoin price prediction
  - Implements attention mechanisms for time series forecasting
  - Offers training and prediction functions

- **src/model_factory.py**
  - Factory pattern for creating and using different model types
  - Supports ensemble models combining multiple approaches
  - Handles model selection and configuration

- **src/technical_indicators.py**
  - Calculates technical analysis indicators (RSI, MACD, Bollinger Bands)
  - Processes Bitcoin price data for technical analysis
  - Provides indicator values for visualization

- **src/utils.py**
  - Utility functions used across the application
  - Includes data formatting, date handling, and mathematical operations
  - Provides helper functions for the UI

- **src/visualizer.py**
  - Data visualization components
  - Creates interactive charts for price data, forecasts, and technical indicators
  - Supports custom styling and interactive elements

### Sentiment Analysis Module (`sentiment_analysis/` directory)

- **sentiment_analysis/sentiment_analyzer.py**
  - Core sentiment analysis functionality
  - Fetches news using NewsAPI
  - Analyzes sentiment using TextBlob
  - Stores results in PostgreSQL database

- **sentiment_analysis/logging_config.py**
  - Configures logging for the sentiment analysis service
  - Handles log levels, file output, and formatting
  - Used by all sentiment analysis components

### Docker Configuration (`docker/` directory)

- **docker/app/Dockerfile**
  - Main application container configuration
  - Sets up Python environment and dependencies
  - Configures Streamlit for web access

- **docker/sentiment/Dockerfile**
  - Sentiment analysis service container configuration
  - Sets up environment for background sentiment processing
  - Configures data and log directories

- **docker/docker-compose.yml**
  - Multi-container deployment configuration
  - Defines services, networks, and volumes
  - Coordinates application, sentiment analysis, and database containers

- **docker/scripts/app_entrypoint.sh**
  - Entry point script for the main application container
  - Ensures database connectivity before starting
  - Initializes required directories and data

- **docker/scripts/sentiment_entrypoint.sh**
  - Entry point script for the sentiment analysis container
  - Sets up database tables if they don't exist
  - Configures background sentiment analysis processing

- **docker/scripts/docker_build.sh**
  - Builds Docker images for all services
  - Sets correct tags and versions
  - Optimizes build process

- **docker/scripts/docker_run.sh**
  - Starts all containers with proper configuration
  - Sets up environment variables
  - Ensures containers are properly networked

- **docker/scripts/docker_stop.sh**
  - Safely stops all running containers
  - Preserves data volumes
  - Cleans up resources

### Database Scripts

- **db_init.sh**
  - Initializes PostgreSQL database tables
  - Creates schema for news articles and sentiment data
  - Sets up indexes and constraints

## API Integration

The system integrates with the following external APIs:

### YFinance API
- Used for retrieving historical Bitcoin price data
- Provides OHLC price information, volume, and other metrics
- No authentication required

### NewsAPI
- Used for gathering Bitcoin-related news articles
- Requires API key (stored in NEWS_API_KEY environment variable)
- Supports querying by keyword, date range, and sorting options
- Free tier limits (100 requests/day, articles up to 30 days old)

## Data Flow

1. **Price Data Collection**
   - YFinance API retrieves historical Bitcoin prices
   - Data is cleaned and processed in data_collector.py
   - Technical indicators are calculated in technical_indicators.py

2. **Sentiment Analysis**
   - NewsAPI fetches Bitcoin-related articles
   - TextBlob analyzes sentiment of article titles and content
   - Results are stored in PostgreSQL and CSV backup files
   - Scheduled jobs update sentiment data hourly and daily

3. **Forecasting**
   - Price data and sentiment indicators are combined
   - Selected model (ARIMA, LSTM, Transformer) makes predictions
   - Forecasts and confidence intervals are calculated
   - Results are visualized in the Streamlit interface

4. **Visualization and UI**
   - Streamlit components render interactive charts
   - User inputs configure models and visualizations
   - Real-time updates refresh data and predictions

## Database Schema

### news_articles Table
- `id`: Unique article identifier
- `source`: News source name
- `title`: Article title
- `description`: Article description
- `url`: Article URL
- `published_at`: Publication timestamp
- `created_at`: Record creation timestamp

### sentiment_analysis Table
- `id`: Unique analysis identifier
- `article_id`: Foreign key to news_articles
- `polarity`: Sentiment polarity score (-1.0 to 1.0)
- `subjectivity`: Sentiment subjectivity score (0.0 to 1.0)
- `created_at`: Analysis timestamp

### aggregate_sentiment Table
- `date`: Aggregation date (daily)
- `avg_polarity`: Average sentiment polarity
- `avg_subjectivity`: Average sentiment subjectivity
- `article_count`: Number of articles analyzed
- `positive_count`: Number of positive articles
- `negative_count`: Number of negative articles
- `neutral_count`: Number of neutral articles