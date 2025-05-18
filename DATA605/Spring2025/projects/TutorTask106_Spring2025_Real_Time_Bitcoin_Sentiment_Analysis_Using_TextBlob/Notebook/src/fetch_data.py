from src.common import NEWS_API_KEY, RELEVANT_SOURCES, newsapi, coingecko, logger
from datetime import datetime, timedelta
import pandas as pd
import time
from src.data_saver import save_data,load_data
import os
from multiprocessing.dummy import Pool as ThreadPool  # uses threads, not processes
from multiprocessing import cpu_count
from src.language_utils import detect_language, translate_text


COLUMNS_TO_TRANSLATE = ['title', 'content', 'description']

def translate_row(row):
    result = {}
    for col in COLUMNS_TO_TRANSLATE:
        original = row.get(col, "")
        if row.get('language') != 'en' and pd.notnull(original):
            result[f'translated_{col}'] = translate_text(original, 'en')
        else:
            result[f'translated_{col}'] = original
    return result

def fetch_bitcoin_news(start_date, end_date, refresh=False):
    """
    Fetch Bitcoin-related news articles from NewsAPI.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        refresh (bool): Ignored, included for interface compatibility

    Returns:
        pandas.DataFrame: DataFrame containing news articles
    """
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')

    today = datetime.now().date()
    earliest_allowed = today - timedelta(days=29)
    if start_dt.date() < earliest_allowed:
        msg = f"Adjusting start date from {start_dt.date()} to {earliest_allowed} due to NewsAPI's 30-day limit"
        logger.warning(msg)
        start_dt = datetime.combine(earliest_allowed, datetime.min.time())

    if not newsapi:
        logger.error("NewsAPI key not available. Please set the NEWS_API_KEY environment variable.")
        return None

    articles = []
    try:
        try:
            key_status = newsapi.get_sources()
            if key_status.get('status') == 'ok':
                logger.info("Using valid NewsAPI key")
        except:
            logger.warning("Unable to verify NewsAPI key")

        current_date = start_dt
        total_articles = 0

        # Break into 1-day chunks to avoid 100 article cap
        while current_date <= end_dt:
            next_date = min(current_date + timedelta(days=1), end_dt)
            from_date = current_date.strftime('%Y-%m-%d')
            to_date = next_date.strftime('%Y-%m-%d')
            sources_param = ','.join(RELEVANT_SOURCES)
            
            try:
                response = newsapi.get_everything(
                    q='bitcoin OR crypto OR cryptocurrency OR BTC',
                    # language='fr', #Getting all languages
                    sources=sources_param,  # <-- NEW: filter by trusted sources
                    from_param=from_date,
                    to=to_date,
                    sort_by='publishedAt',
                    page=1,  # Only page 1 to avoid hitting free-tier limit
                    page_size=100
                )

                

                if response.get('articles'):
                    batch_articles = [{
                        'title': a.get('title', ''),
                        'description': a.get('description', ''),
                        'content': a.get('content', ''),
                        'source': a.get('source', {}).get('name', 'Unknown'),
                        'author': a.get('author', 'Unknown'),
                        'url': a.get('url', ''),
                        'publishedAt': a.get('publishedAt', '')
                    } for a in response['articles']]

                    articles.extend(batch_articles)
                    total_articles += len(batch_articles)

                    if len(batch_articles) == 100:
                        logger.warning(f"Hit 100-article cap for {from_date}. More articles likely exist but are not retrievable with free tier.")

                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"Error fetching news for {from_date} to {to_date}: {str(e)}")

            current_date = next_date + timedelta(days=1)
            time.sleep(0.5)

        if articles:
            try:
                df_1 = load_data('bitcoin_news.csv')
            except:
                df_1 = pd.DataFrame()
            
           
            

            df_2 = pd.DataFrame(articles)
            df = pd.concat([df_1, df_2])
            df ['language'] = df['content'].apply(lambda x: detect_language(x))
            
            # Threaded parallelism
            pool = ThreadPool()#cpu_count()  
            results = pool.map(translate_row, df.to_dict(orient='records'))
            pool.close()
            pool.join()

            translated_df = pd.DataFrame(results)
            df = pd.concat([df, translated_df], axis=1)
            save_data(df, 'bitcoin_news_original_translated.csv', include_timestamp=False)
            new_df = pd.DataFrame({
                'title': df['translated_title'],
                'description': df['translated_description'], 
                'content': df['translated_content'],
                'source': df['source'],
                'author': df['author'],
                'url': df['url'],
                'publishedAt': df['publishedAt'],
                'language': df['language']
            })
            df = new_df


            save_data(df, 'bitcoin_news.csv', include_timestamp=False)

            df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors='coerce')
            df['date'] = df['publishedAt'].dt.date
            filtered_df = df[(df['date'] >= start_dt.date()) & (df['date'] <= end_dt.date())]
            logger.info(f"Retrieved {len(filtered_df)} articles from NewsAPI for {start_date} to {end_date}")
            return filtered_df
        else:
            logger.warning("No articles found for the specified date range.")
            return None

    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return None
    

def fetch_bitcoin_prices(start_date, end_date, refresh=False):
    """
    Fetch Bitcoin historical price data from CoinGecko API.
    
    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        refresh (bool): Currently unused; all data is fetched fresh from API
    
    Returns:
        pandas.DataFrame: DataFrame containing price data
    """
    try:
        # Convert date strings to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Convert date strings to unix timestamps (required by CoinGecko)
        start_timestamp = int(start_dt.timestamp())
        end_timestamp = int(end_dt.timestamp()) + 86400  # Add one day to include end_date
        
        msg = "Fetching Bitcoin price data from CoinGecko API..."
        logger.info(msg)
        logger.info(msg)
        
        # Fetch data
        market_data = coingecko.get_coin_market_chart_range_by_id(
            id='bitcoin',
            vs_currency='usd',
            from_timestamp=start_timestamp,
            to_timestamp=end_timestamp
        )
        
        prices_data = market_data.get('prices', [])
        
        if prices_data:
            # Convert to DataFrame
            df = pd.DataFrame(prices_data, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['hour'] = df['timestamp'].dt.floor('H')
            
            # Aggregate by hour
            hourly_prices = df.groupby('hour').agg(
                open_price=('price', 'first'),
                close_price=('price', 'last'),
                high_price=('price', 'max'),
                low_price=('price', 'min'),
                avg_price=('price', 'mean')
            ).reset_index()
            hourly_prices = hourly_prices.rename(columns={'hour': 'date'})
            
            # Add percentage change
            hourly_prices['price_change_pct'] = hourly_prices['close_price'].pct_change() * 100
            
            logger.info(f"Retrieved Bitcoin price data for {len(hourly_prices)} hours.")
            return hourly_prices
        else:
            msg = "No price data found for the specified date range."
            logger.warning(msg)
            logger.warning(msg)
            return None

    except Exception as e:
        error_msg = f"Error fetching Bitcoin prices: {str(e)}"
        logger.error(error_msg)
        logger.error(error_msg)
        return None
        