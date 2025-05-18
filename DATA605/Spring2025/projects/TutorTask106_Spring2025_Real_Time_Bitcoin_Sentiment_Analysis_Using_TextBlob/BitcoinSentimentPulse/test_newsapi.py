import os
from newsapi.newsapi_client import NewsApiClient
import datetime

def test_newsapi():
    """Test if NewsAPI is working properly"""
    api_key = os.environ.get('NEWS_API_KEY')
    if not api_key:
        print("NewsAPI key not found in environment variables")
        return
    
    try:
        # Initialize NewsAPI client
        newsapi = NewsApiClient(api_key=api_key)
        
        # Set date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=7)
        
        # Format dates for NewsAPI
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        
        # Search terms for Bitcoin
        search_terms = 'bitcoin OR cryptocurrency OR crypto OR BTC'
        
        # Fetch news articles
        print(f"Fetching Bitcoin news from {from_date} to {to_date}...")
        news_response = newsapi.get_everything(
            q=search_terms,
            from_param=from_date,
            to=to_date,
            language='en',
            sort_by='publishedAt',
            page_size=10
        )
        
        if news_response.get('status') == 'ok':
            articles = news_response.get('articles', [])
            print(f"Found {len(articles)} articles")
            
            # Print first article title for verification
            if articles:
                print("\nFirst article:")
                print(f"Title: {articles[0].get('title')}")
                print(f"Source: {articles[0].get('source', {}).get('name')}")
                print(f"Published: {articles[0].get('publishedAt')}")
            
            return True
        else:
            error_msg = news_response.get('message', 'Unknown error')
            print(f"NewsAPI error: {error_msg}")
            return False
    
    except Exception as e:
        print(f"Error testing NewsAPI: {str(e)}")
        return False

if __name__ == "__main__":
    test_newsapi()