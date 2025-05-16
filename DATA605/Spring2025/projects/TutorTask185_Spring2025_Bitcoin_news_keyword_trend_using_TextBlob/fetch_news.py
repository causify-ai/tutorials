import os
from datetime import datetime, timedelta
import pandas as pd
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException
from dotenv import load_dotenv
import time

# Load environment variables from .env file
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Error loading .env file: {e}")
    print("Attempting to set API key directly...")
    try:
        with open('.env', 'r', encoding='utf-8-sig') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except Exception as e2:
        print(f"Error setting API key: {e2}")

def fetch_bitcoin_news(days=7, query='bitcoin OR cryptocurrency', language='en', sleep_between_days=0.5):
    """
    Fetch Bitcoin-related news articles using NewsAPI, one day at a time to manage rate limits.
    
    Args:
        days (int): Number of days to fetch articles for
        query (str): Search query to use for finding articles
        language (str): Language code (e.g., 'en' for English)
        sleep_between_days (float): Time to sleep between API calls to avoid rate limits
        
    Returns:
        pandas.DataFrame: DataFrame containing news articles
    """
    try:
        # Try to get API key from environment
        api_key = os.getenv('NEWSAPI_KEY')
        
        # If no API key found, try to use a hardcoded demo key
        if not api_key or api_key == "your_api_key_here":
            print("u274c NewsAPI key not found or using placeholder. Using demo key.")
            api_key = "YOUR_DEMO_API_KEY"  # Replace with a demo key if available
            
        if not api_key or api_key == "YOUR_DEMO_API_KEY":
            print("u274c No usable NewsAPI key found. Please add NEWSAPI_KEY to your .env file.")
            print("    You can get a key at: https://newsapi.org/")
            return None

        # Initialize NewsAPI client
        newsapi = NewsApiClient(api_key=api_key)
        all_articles = []
        
        print(f"ud83dudcac Using search query: '{query}'")
        print(f"ud83dudcc5 Fetching news for the past {days} days")

        # Fetch articles one day at a time to manage API rate limits
        for i in range(days):
            # Calculate date range for this iteration
            day = datetime.now() - timedelta(days=i)
            from_date = day.strftime('%Y-%m-%d')
            to_date = (day + timedelta(days=1)).strftime('%Y-%m-%d')
            
            try:
                # Make API request
                print(f"  \u2192 Fetching articles for {from_date}...")
                articles = newsapi.get_everything(
                    q=query,
                    from_param=from_date,
                    to=to_date,
                    language=language,
                    sort_by='publishedAt',
                    page_size=100  # Maximum allowed by API
                )
                
                # Process results
                if articles.get('articles'):
                    for article in articles['articles']:
                        article['fetched_date'] = from_date
                    all_articles.extend(articles['articles'])
                    print(f"    \u2713 Found {len(articles['articles'])} articles")
                else:
                    print(f"    \u2713 No articles found for {from_date}")
                    
                # Sleep between requests to avoid hitting rate limits
                if i < days - 1 and sleep_between_days > 0:
                    time.sleep(sleep_between_days)
                    
            except NewsAPIException as e:
                if "426" in str(e) or "429" in str(e):
                    print(f"\u26a0\ufe0f API rate limit reached. Using data collected so far.")
                    break
                else:
                    print(f"\u26a0\ufe0f Error fetching news for {from_date}: {str(e)}")
                    continue

        # Check if we have any articles
        if not all_articles:
            print("\u274c No articles found. This could be due to API rate limits or no matching content.")
            return None

        # Convert to DataFrame and process
        df = pd.DataFrame(all_articles)
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        df['date'] = df['publishedAt'].dt.date
        df['hour'] = df['publishedAt'].dt.hour
        
        # Remove duplicates (sometimes the API returns the same article multiple times)
        initial_count = len(df)
        df = df.drop_duplicates(subset=['title', 'url'])
        if initial_count > len(df):
            print(f"\ud83d\udcca Removed {initial_count - len(df)} duplicate articles")

        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Save to CSV
        try:
            df.to_csv('data/bitcoin_news.csv', index=False, encoding='utf-8')
            print(f"\u2705 Successfully fetched {len(df)} unique news articles over {days} days")
        except UnicodeEncodeError:
            # Handle Unicode encoding issues
            print("\u26a0\ufe0f Unicode encoding issues detected. Trying alternative encoding...")
            try:
                # Replace problematic Unicode characters
                for col in df.select_dtypes(include=['object']).columns:
                    df[col] = df[col].astype(str).apply(lambda x: x.encode('ascii', 'replace').decode('ascii'))
                df.to_csv('data/bitcoin_news.csv', index=False, encoding='ascii')
                print(f"\u2705 Successfully saved data with alternative encoding")
            except Exception as e3:
                print(f"\u26a0\ufe0f Error saving with alternative encoding: {str(e3)}")
                # As a last resort, save only essential columns
                try:
                    essential_df = df[['title', 'description', 'publishedAt', 'date', 'hour']].copy()
                    essential_df.to_csv('data/bitcoin_news.csv', index=False, encoding='ascii', errors='replace')
                    print(f"\u2705 Saved simplified data after encoding issues")
                except Exception as e4:
                    print(f"\u274c Could not save data: {str(e4)}")
        
        # Print some sample titles
        print("\n\ud83d\udcac Sample article titles:")
        for title in df['title'].head(5).tolist():
            print(f"  \u2022 {title}")
        
        return df

    except Exception as e:
        print(f"\u274c Error fetching news: {str(e)}")
        return None

def create_query(keywords=None, include_crypto=True, include_bitcoin=True):
    """
    Create a search query for the NewsAPI based on keywords and options.
    
    Args:
        keywords (list): Additional keywords to include in the search
        include_crypto (bool): Whether to include cryptocurrency-related terms
        include_bitcoin (bool): Whether to include Bitcoin-related terms
        
    Returns:
        str: Formatted search query string
    """
    query_parts = []
    
    # Add Bitcoin terms if requested
    if include_bitcoin:
        query_parts.append('bitcoin OR btc')
    
    # Add cryptocurrency terms if requested
    if include_crypto:
        query_parts.append('cryptocurrency OR crypto OR blockchain')
    
    # Add custom keywords if provided
    if keywords and isinstance(keywords, list) and len(keywords) > 0:
        keyword_query = ' OR '.join(keywords)
        query_parts.append(f'({keyword_query})')
    
    # Join all parts with OR
    if query_parts:
        return ' OR '.join(query_parts)
    else:
        return 'bitcoin OR cryptocurrency'  # Default fallback

if __name__ == "__main__":
    # Test the function with a smaller number of days for quick testing
    print("\ud83d\udd0e TESTING NEWS API FETCHING")
    print("=" * 50)
    
    # Ask for custom query or use default
    custom_query = input("Enter a custom search query (or press Enter for default): ").strip()
    days = int(input("How many days to fetch (1-30): ") or "3")
    
    if custom_query:
        fetch_bitcoin_news(days=days, query=custom_query)
    else:
        # Use the default query
        fetch_bitcoin_news(days=days)