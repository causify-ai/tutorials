import os
import pandas as pd
from datetime import datetime
from googletrans import Translator

def save_intermediate_data(data, filename, data_type='original'):
    """Save intermediate data to CSV with support for translations.
    
    Args:
        data (pandas.DataFrame): Data to save
        filename (str): Base filename
        data_type (str): Type of data ('original' or 'translated')
    """
    if data is None or data.empty:
        return
    
    try:
        os.makedirs('data', exist_ok=True)
        data_copy = data.copy()
        
        # Format datetime columns
        if 'date' in data_copy.columns and pd.api.types.is_datetime64_any_dtype(data_copy['date']):
            data_copy['date'] = data_copy['date'].dt.strftime('%Y-%m-%d')
        if 'publishedAt' in data_copy.columns and pd.api.types.is_datetime64_any_dtype(data_copy['publishedAt']):
            data_copy['publishedAt'] = data_copy['publishedAt'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Construct filename based on data type
        base, ext = os.path.splitext(filename)
        if data_type == 'translated':
            filename = f"{base}_translated{ext}"
        else:
            filename = f"{base}_original{ext}"
        
        filepath = os.path.join('data', filename)
        
        # If file exists, append new data
        if os.path.exists(filepath):
            existing_data = pd.read_csv(filepath)
            # Remove duplicates based on date and content
            combined_data = pd.concat([existing_data, data_copy])
            combined_data = combined_data.drop_duplicates(subset=['date', 'content'], keep='last')
            combined_data.to_csv(filepath, index=False)
        else:
            data_copy.to_csv(filepath, index=False)
            
    except Exception as e:
        print(f"Error saving intermediate data: {str(e)}")

def translate_text(text, target_language='es'):
    """Translate text to target language using Google Translate API.
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (default: 'es' for Spanish)
    """
    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text

def process_and_save_news_data(df):
    """Process news data and save both original and translated versions.
    
    Args:
        df (pandas.DataFrame): News data to process and save
    """
    if df is None or df.empty:
        return
    
    # Save original data
    save_intermediate_data(df, 'bitcoin_news.csv', 'original')
    
    # Create and save translations
    df_translated = df.copy()
    df_translated['title_translated'] = df_translated['title'].apply(lambda x: translate_text(x) if isinstance(x, str) else x)
    df_translated['description_translated'] = df_translated['description'].apply(lambda x: translate_text(x) if isinstance(x, str) else x)
    df_translated['content_translated'] = df_translated['content'].apply(lambda x: translate_text(x) if isinstance(x, str) else x)
    
    save_intermediate_data(df_translated, 'bitcoin_news.csv', 'translated')

def process_and_save_price_data(df):
    """Process price data and save to CSV.
    
    Args:
        df (pandas.DataFrame): Price data to process and save
    """
    if df is None or df.empty:
        return
    
    save_intermediate_data(df, 'bitcoin_prices.csv', 'original') 