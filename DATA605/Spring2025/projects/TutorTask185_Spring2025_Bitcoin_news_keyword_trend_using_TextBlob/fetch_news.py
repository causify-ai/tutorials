import os
from datetime import datetime, timedelta
import pandas as pd
from newsapi import NewsApiClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fetch_bitcoin_news(days=7):
    """
    Fetch Bitcoin-related news articles using NewsAPI, one day at a time.
    """
    try:
        api_key = os.getenv('NEWSAPI_KEY')
        
        if not api_key:
            print("❌ NewsAPI key not found in environment variables. Please add NEWSAPI_KEY to your .env file.")
            return None

        newsapi = NewsApiClient(api_key=api_key)
        all_articles = []

        for i in range(days):
            day = datetime.now() - timedelta(days=i)
            from_date = day.strftime('%Y-%m-%d')
            to_date = (day + timedelta(days=1)).strftime('%Y-%m-%d')
            articles = newsapi.get_everything(
                q='bitcoin OR cryptocurrency',
                from_param=from_date,
                to=to_date,
                language='en',
                sort_by='publishedAt',
                page_size=100
            )
            if articles.get('articles'):
                for article in articles['articles']:
                    article['fetched_date'] = from_date
                all_articles.extend(articles['articles'])

        if not all_articles:
            print("No articles found")
            return None

        df = pd.DataFrame(all_articles)
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        df['date'] = df['publishedAt'].dt.date
        df['hour'] = df['publishedAt'].dt.hour

        os.makedirs('data', exist_ok=True)
        df.to_csv('data/bitcoin_news.csv', index=False)
        print(f"✅ Successfully fetched {len(df)} news articles over {days} days")
        return df

    except Exception as e:
        print(f"❌ Error fetching news: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the function
    fetch_bitcoin_news()