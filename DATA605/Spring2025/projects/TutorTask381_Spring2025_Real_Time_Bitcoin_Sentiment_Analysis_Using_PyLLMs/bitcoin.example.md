# Bitcoin News Sentiment Analysis: Real-World Examples

This guide demonstrates practical applications of the Bitcoin News Sentiment Analysis tool for real-world scenarios.

## Use Case: Scheduling Hourly Sentiment Logging for a Dashboard

A common use case is to continuously monitor Bitcoin news sentiment and feed the data into a live dashboard. This allows traders and analysts to track sentiment shifts in near real-time.

### Setting Up Scheduled Runs

The script supports automated hourly runs with caching to prevent redundant API calls:

```python
# Create a simple scheduled script
import argparse
from bitcoin_utils import Config
from bitcoin_news_sentiment import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bitcoin News Sentiment Monitor")
    parser.add_argument("--loop", action="store_true", help="Run continuously on schedule")
    parser.add_argument("--provider", default="together_ai", 
                       choices=["together_ai", "ollama", "openai", "huggingface", "gemini"],
                       help="LLM provider to use")
    parser.add_argument("--interval", type=int, default=60,
                       help="Minutes between runs (default: 60)")
    
    args = parser.parse_args()
    
    if args.loop:
        import schedule
        import time
        
        config = Config.load()
        config.PROVIDER = args.provider
        
        def run_job():
            print(f"Running scheduled sentiment analysis at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            main()
        
        # Schedule the job
        schedule.every(args.interval).minutes.do(run_job)
        
        # Run immediately on startup
        run_job()
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        # Run once
        main()
```

Save this as `schedule_sentiment.py` and run with:

```bash
# For a one-time run:
python schedule_sentiment.py

# For continuous hourly updates:
python schedule_sentiment.py --loop

# For continuous updates every 30 minutes using OpenAI:
python schedule_sentiment.py --loop --interval 30 --provider openai
```

### Setting Up as a System Service

For production deployments, you can set this up as a system service:

#### Linux (systemd)

```
[Unit]
Description=Bitcoin News Sentiment Monitor
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/bitcoin-sentiment
ExecStart=/usr/bin/python3 /path/to/bitcoin-sentiment/schedule_sentiment.py --loop
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save this to `/etc/systemd/system/bitcoin-sentiment.service` and run:

```bash
sudo systemctl enable bitcoin-sentiment
sudo systemctl start bitcoin-sentiment
```

## Visualizing the CSV Data

The sentiment data is saved to CSV in the `data` folder. Here are some ways to visualize it:

### Quick Interactive Dashboard with Plotly Dash

```python
# dashboard.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

# Initialize the app
app = dash.Dash(__name__, title="Bitcoin Sentiment Dashboard")

# Define the layout
app.layout = html.Div([
    html.H1("Bitcoin News Sentiment Dashboard"),
    
    html.Div([
        html.Button('Refresh Data', id='refresh-button', n_clicks=0),
        html.Div(id='last-update-time')
    ]),
    
    dcc.Graph(id='sentiment-timeline'),
    
    dcc.Graph(id='sentiment-distribution'),
    
    html.H3("Latest Bitcoin News Articles"),
    html.Div(id='news-table')
])

# Define callbacks
@app.callback(
    [Output('sentiment-timeline', 'figure'),
     Output('sentiment-distribution', 'figure'),
     Output('news-table', 'children'),
     Output('last-update-time', 'children')],
    [Input('refresh-button', 'n_clicks')]
)
def update_dashboard(n_clicks):
    # Load the data
    csv_path = Path.cwd() / "data" / "bitcoin_sentiment_results.csv"
    df = pd.read_csv(csv_path)
    df['publishedAt'] = pd.to_datetime(df['publishedAt'])
    
    # Sort by date
    df = df.sort_values('publishedAt')
    
    # Create sentiment timeline
    timeline_fig = px.line(
        df, x='publishedAt', y='score', 
        title='Bitcoin News Sentiment Over Time',
        labels={'score': 'Sentiment Score (-1=Negative, 0=Neutral, 1=Positive)', 'publishedAt': 'Date'}
    )
    timeline_fig.update_layout(hovermode='x unified')
    
    # Create sentiment distribution
    pie_fig = px.pie(
        values=df['sentiment'].value_counts().values, 
        names=df['sentiment'].value_counts().index,
        title='Sentiment Distribution',
        color=df['sentiment'].value_counts().index,
        color_discrete_map={'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
    )
    
    # Create news table
    recent_news = df.sort_values('publishedAt', ascending=False).head(10)
    news_table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in ['Date', 'Headline', 'Sentiment']])] +
        # Body
        [html.Tr([
            html.Td(article['publishedAt'].strftime('%Y-%m-%d %H:%M')),
            html.Td(html.A(article['headline'][:100] + '...', href=article['url'], target='_blank')),
            html.Td(article['sentiment'], style={'color': 
                                               'green' if article['sentiment'] == 'Positive' else 
                                               'red' if article['sentiment'] == 'Negative' else 'gray'})
        ]) for _, article in recent_news.iterrows()]
    )
    
    last_update = f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return timeline_fig, pie_fig, news_table, last_update

if __name__ == '__main__':
    app.run_server(debug=True)
```

Run this with:

```bash
pip install dash
python dashboard.py
```

Then visit http://localhost:8050 in your browser.

### Simple Matplotlib Visualization

For a quick static visualization without a web server:

```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load data
csv_path = Path.cwd() / "data" / "bitcoin_sentiment_results.csv"
df = pd.read_csv(csv_path)
df['publishedAt'] = pd.to_datetime(df['publishedAt'])

# Sort by date
df = df.sort_values('publishedAt')

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# 1. Sentiment timeline
df['score'].rolling(window=5).mean().plot(
    ax=ax1, title='Bitcoin News Sentiment (5-article rolling average)'
)
ax1.axhline(y=0, color='gray', linestyle='--')
ax1.set_ylabel('Sentiment Score')

# 2. Sentiment distribution
sentiment_counts = df['sentiment'].value_counts()
ax2.pie(
    sentiment_counts.values, 
    labels=sentiment_counts.index,
    autopct='%1.1f%%', 
    colors=['green', 'gray', 'red']
)
ax2.set_title('Sentiment Distribution')

plt.tight_layout()
plt.savefig('sentiment_summary.png')
plt.show()
```

## Customization Tips

### Date Range Customization

You can customize the date range for fetching articles:

```python
# Fetch articles from a specific date range
from datetime import datetime, timedelta
from bitcoin_utils import Config, process_news_articles

config = Config.load()

# Last 7 days
df_week = process_news_articles(config, days_back=7)

# Last 30 days
df_month = process_news_articles(config, days_back=30)

# Custom date range
df_custom = process_news_articles(
    config, 
    custom_from_date="2023-01-01", 
    custom_to_date="2023-01-31"
)

# Increase results (up to 100 per request with NewsAPI)
df_more = process_news_articles(config, page_size=50, days_back=3)
```

### Switching LLM Providers

The system supports multiple LLM providers. You can switch between them:

```python
from bitcoin_utils import Config, process_news_articles

# Load config
config = Config.load()

# Use OpenAI
config.PROVIDER = "openai"
df_openai = process_news_articles(config)

# Use Together.ai
config.PROVIDER = "together_ai"
df_together = process_news_articles(config)

# Use local Ollama (no API key required, but must have Ollama installed)
config.PROVIDER = "ollama"
df_ollama = process_news_articles(config)

# Use Google Gemini
config.PROVIDER = "gemini"
df_gemini = process_news_articles(config)
```

### Modifying the Prompt

You can customize the sentiment analysis prompt by modifying the `PROMPT_TEMPLATE` in the config:

```python
from bitcoin_utils import Config, process_news_articles

# Load config
config = Config.load()

# Modify prompt to have more detailed sentiment
config.PROMPT_TEMPLATE = (
    "You are a financial sentiment analyst with deep expertise in cryptocurrency markets.\n"
    "Analyze the sentiment of the following Bitcoin news article and classify it as one of:\n"
    "'Very Positive', 'Positive', 'Neutral', 'Negative', 'Very Negative'.\n\n"
    "Respond with ONLY the sentiment classification (e.g., 'Positive').\n\n"
    "Article: {text}\n\nSentiment:"
)

# Process with custom prompt
df = process_news_articles(config)
```

### Exporting to Other Formats

The data can be exported to various formats for different visualization tools:

```python
from bitcoin_utils import Config, process_news_articles
import pandas as pd
from pathlib import Path

# Get sentiment data
config = Config.load()
df = process_news_articles(config, days_back=7)

# Export directory
export_dir = Path.cwd() / "exports"
export_dir.mkdir(exist_ok=True)

# Export to Excel
df.to_excel(export_dir / "bitcoin_sentiment.xlsx", index=False)

# Export to JSON
df.to_json(export_dir / "bitcoin_sentiment.json", orient="records")

# Export summary statistics
sentiment_counts = df['sentiment'].value_counts().to_dict()
with open(export_dir / "sentiment_summary.json", "w") as f:
    import json
    json.dump({
        "total_articles": len(df),
        "sentiment_counts": sentiment_counts,
        "average_score": df['score'].mean(),
        "date_range": {
            "start": df['publishedAt'].min().strftime('%Y-%m-%d'),
            "end": df['publishedAt'].max().strftime('%Y-%m-%d')
        }
    }, f, indent=2)
```

This allows integration with tools like Tableau, PowerBI, or custom dashboards. 