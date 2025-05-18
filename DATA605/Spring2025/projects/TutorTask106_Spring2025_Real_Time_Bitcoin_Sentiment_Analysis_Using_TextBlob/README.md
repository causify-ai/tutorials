# Bitcoin Sentiment Pulse

A comprehensive Bitcoin price forecasting and sentiment analysis platform that combines technical analysis with news sentiment to provide more accurate price predictions.

## Project Structure

The project is organized into two main components:

### 1. Main Application (`BitcoinSentimentPulse/`)

The main application provides:
- Real-time Bitcoin price forecasting using multiple models (LSTM, Prophet, ARIMA)
- Interactive visualizations of price predictions and confidence intervals
- Technical analysis indicators and metrics
- User-friendly interface for model parameter tuning
- Historical data analysis and comparison

Key features:
- Multiple forecasting models with customizable parameters
- Integration with sentiment analysis data
- Real-time data updates
- Interactive charts and visualizations
- Technical analysis tools

### 2. Notebook (`Notebook/`)

Contains Jupyter notebooks for:
- Data exploration and analysis
- Model development and testing
- Sentiment analysis implementation
- Visualization development
- Experimental results and findings

## Architecture

The project uses:
- Python-based implementation
- PostgreSQL database for data storage
- RESTful APIs for service communication
- Streamlit for the web interface

## Getting Started

1. Clone the repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL database
4. Run the application:
   ```bash
   streamlit run BitcoinSentimentPulse/app.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 