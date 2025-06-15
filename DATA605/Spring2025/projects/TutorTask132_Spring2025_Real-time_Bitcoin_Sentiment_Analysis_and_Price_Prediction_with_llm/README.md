# Real-Time Bitcoin Sentiment Analysis and Price Prediction with LLM

**Author**: Rishika Thakre 
**Date**: 2025-05-17  
**Course**: DATA605 — Spring 2025

---

## 1. Project Overview

This project builds an end-to-end pipeline to:

1. Ingest real-time Bitcoin-related text data (News, Twitter, Reddit)
2. Use NewsAPI to extract all the news articles
3. Perform sentiment analysis using LLMs (via OpenAI)
4. Aggregate results into a sentiment time series
5. Predict future Bitcoin prices using multiple models:
   - Linear Regression
   - Prophet
   - LSTM Neural Networks
6. Visualize trends and analysis results

There are two primary entry points:

- **`bitcoin_llm.API.ipynb`** — demonstration of core API interactions  
- **`bitcoin_llm.example.ipynb`** — end-to-end pipeline runner  

For interactive, cell-by-cell exploration, see the companion notebooks.

---

## 2. Project Files

```text
bitcoin_llm_utils.py           # shared helpers for API, data fetch, modeling, plotting
bitcoin_llm.API.ipynb          # interactive API walkthrough
bitcoin_llm.API.md             # markdown docs for API.ipynb
bitcoin_llm.example.ipynb      # interactive pipeline walkthrough
bitcoin_llm.example.md         # markdown docs for example.ipynb

news_data/                     # stored news articles from NewsAPI
  └─ bitcoin_news_final_*.json # timestamped raw news data

sentiment_data/               # processed sentiment analysis results
  ├─ bitcoin_news_sentiment_*.json  # timestamped sentiment results
  ├─ daily_sentiment_counts.csv     # aggregated daily counts
  └─ daily_sentiment_percent.csv    # aggregated daily percentages

merged_data/                  # combined price and sentiment data
  └─ sentiment_price_data.csv # merged dataset for modeling

scripts/                      # auxiliary shell scripts
requirements.txt              # Python dependencies
Dockerfile                    # image spec (DATA605 style)
docker_build.sh              # build image
docker_bash.sh               # start bash shell
docker_jupyter.sh            # launch JupyterLab
docker_name.sh               # tagging helper
```

---

## 3. Prerequisites & Setup

1. **Clone the repo & navigate**  
   ```bash
   git clone https://github.com/causify-ai/tutorials.git
   cd tutorials/DATA605/Spring2025/projects/TutorTask132_Spring2025_Real-time_Bitcoin_Sentiment_Analysis_and_Price_Prediction_with_llm
   ```
2. **Install Docker** (Desktop/Engine)  
3. **Get API Keys**:
   - NewsAPI Key
   - OpenAI API Key
4. **Python 3.10+** with required packages

---

## 4. Build & Run Docker (data605_style)

**Note**: The project includes `install_jupyter_extensions.sh` & `bashrc` for proper Docker setup.

1. **Build the image**  
   ```bash
   chmod +x docker_*.sh
   ./docker_build.sh
   ```
2. **Start an interactive shell** (with API keys mounted)  
   ```bash
   ./docker_bash.sh
   ```
3. **Launch JupyterLab**  
   ```bash
   ./docker_jupyter.sh
   ```
   Open any of the links generated in the browser and run the files.

> **Tip:** You can pass API keys as environment variables:
> ```bash
> docker run --rm -it \
>   -e NEWS_API_KEY="your_key_here" \
>   -e OPENAI_API_KEY="your_key_here" \
>   -v "$(pwd)":/data -p 8888:8888 \
>   umd_data605/bitcoin_llm_project \
>   bash
> ```

---

## 5. Usage

### 5.1 Data Collection
Run the news fetching cells in `bitcoin_llm.example.ipynb` to:
- Fetch latest Bitcoin news
- Store in timestamped JSON files

### 5.2 Sentiment Analysis
Continue with the sentiment analysis cells to:
- Process news articles with OpenAI
- Generate sentiment scores
- Aggregate daily statistics

### 5.3 Price Prediction
Execute the modeling cells to run:
- Linear Regression (sentiment-based)
- Prophet (time series forecasting)
- LSTM (deep learning prediction)

---

## 6. Interactive Notebooks

Open in JupyterLab and **Restart & Run All**:
- `bitcoin_llm.API.ipynb`
- `bitcoin_llm.example.ipynb`

The notebooks include detailed markdown explanations and visualizations for each step.

## 7. Streamlit Visualization

```bash
./docker_bash.sh
cd /data
streamlit run app.py
```

## 8. References

- [NewsAPI Documentation](https://newsapi.org/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Prophet Documentation](https://facebook.github.io/prophet/docs/quick_start.html)
- [Keras LSTM Guide](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM)
