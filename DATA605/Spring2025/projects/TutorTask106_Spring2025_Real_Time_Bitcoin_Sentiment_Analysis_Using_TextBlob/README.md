# Real-Time Bitcoin Sentiment Analysis Using TextBlob

This repository contains the implementation and analysis of a real-time Bitcoin sentiment analysis system using TextBlob for natural language processing. The project demonstrates how to analyze Bitcoin-related news and social media content to gauge market sentiment.

## Project Structure

### 1. Notebook Directory
Contains Jupyter notebooks and Python scripts for Bitcoin sentiment analysis:

#### Main Analysis Notebooks:
- `BitcoinSentimentAnalysis.ipynb`: Basic sentiment analysis implementation
- `Advanced_BitCoin_Sentiment.ipynb`: Advanced sentiment analysis with detailed metrics
- `Bitcoin_Sentiment_Pipeline.ipynb`: Complete sentiment analysis pipeline
- `BitSense_Analysis.ipynb`: BitSense API implementation and analysis

#### API Implementation:
- `BitSense.API.py`: Core API implementation
- `BitSense2.API.ipynb`: Enhanced API version with additional features
- `BitSense_utils.py`: Utility functions for the BitSense API

#### Example and Documentation:
- `BitSense.example.ipynb`: Example usage of the BitSense API
- `BitSense.example.md`: Documentation for the example implementation
- `BitSense.API.md`: API documentation

### 2. Data Directories
Multiple data directories containing:
- Historical Bitcoin price data
- News articles and social media content
- Sentiment analysis results
- Log files

### 3. BitcoinSentimentPulse
A production-ready implementation of the sentiment analysis system with:
- Docker containerization
- Real-time data processing
- Web interface
- Database integration

## Key Features

1. **Real-time Sentiment Analysis**
   - News article processing
   - Social media content analysis
   - Sentiment scoring using TextBlob

2. **Data Processing Pipeline**
   - Data collection and cleaning
   - Text preprocessing
   - Sentiment calculation
   - Results aggregation

3. **API Implementation**
   - RESTful API endpoints
   - Real-time data access
   - Historical data retrieval
   - Sentiment metrics calculation

4. **Visualization and Analysis**
   - Sentiment trends
   - Price correlation analysis
   - Market impact assessment
   - Interactive dashboards

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r Notebook/requirements.txt
   ```

2. Run the example notebook:
   ```bash
   jupyter notebook Notebook/BitSense.example.ipynb
   ```

3. Explore the advanced analysis:
   ```bash
   jupyter notebook Notebook/Advanced_BitCoin_Sentiment.ipynb
   ```

## Dependencies

- Python 3.9+
- TextBlob
- Pandas
- NumPy
- Jupyter
- Matplotlib
- Seaborn
- Requests
- BeautifulSoup4

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 