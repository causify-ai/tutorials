import os
import pandas as pd
from datetime import datetime
from src.logger import get_logger

logger = get_logger(__name__)


def save_data(data, filename, include_timestamp=False, compress=False):
    """
    Save data to a CSV file.

    Args:
        data (pandas.DataFrame): Data to save
        filename (str): Name of the file to save to (e.g., 'bitcoin_prices.csv')
        include_timestamp (bool): Whether to append a timestamp to the filename
        compress (bool): If True, save as .csv.gz compressed file
    """
    if data is None or data.empty:
        return

    try:
        os.makedirs('data', exist_ok=True)
        data_copy = data.copy()

        # Format datetime columns for consistency
        if 'date' in data_copy.columns and pd.api.types.is_datetime64_any_dtype(data_copy['date']):
            data_copy['date'] = data_copy['date'].dt.strftime('%Y-%m-%d')

        if 'publishedAt' in data_copy.columns and pd.api.types.is_datetime64_any_dtype(data_copy['publishedAt']):
            data_copy['publishedAt'] = data_copy['publishedAt'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Add timestamp if required
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{timestamp}{ext}"

        filepath = os.path.join('data', filename)

        # Handle compression
        if compress:
            filepath += '.gz'
            data_copy.to_csv(filepath, index=False, compression='gzip')
        else:
            data_copy.to_csv(filepath, index=False)

        logger.info(f"Saved data to {filepath}")
    except Exception as e:
        logger.warning(f"Error saving data to {filename}: {str(e)}")
        logger.error(f"Error saving data: {str(e)}")


def detect_delimiter_and_encoding(filepath):
    """
    Detect CSV delimiter and file encoding.

    Args:
        filepath (str): Path to the CSV file

    Returns:
        tuple: (delimiter, encoding)
    """
    try:
        with open(filepath, 'rb') as f:
            encoding = chardet.detect(f.read())['encoding']
        with open(filepath, 'r', encoding=encoding) as f:
            sample = f.readline()
            delimiter = csv.Sniffer().sniff(sample).delimiter
        return delimiter, encoding
    except Exception:
        return ',', 'utf-8'  # Fallback


def load_data(filename, compressed=False):
    """
    Load data from a CSV file.

    Args:
        filename (str): Name of the file to load from (e.g., 'bitcoin_prices.csv')
        compressed (bool): If True, expects a .csv.gz file

    Returns:
        pandas.DataFrame or None: Loaded DataFrame or None if file doesn't exist
    """
    try:
        filepath = os.path.join('data', filename)
        if compressed:
            filepath += '.gz'

        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return None

        delimiter, encoding = detect_delimiter_and_encoding(filepath)
        data = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding, compression='gzip' if compressed else None)

        # Convert date columns
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'], errors='coerce')
            data = data.dropna(subset=['date'])

        if 'publishedAt' in data.columns:
            data['publishedAt'] = pd.to_datetime(data['publishedAt'], errors='coerce')

        logger.info(f"Loaded data from {filepath}")
        return data
    except Exception as e:
        logger.warning(f"Error loading data from {filename}: {str(e)}")
        logger.error(f"Error loading data: {str(e)}")
        return None


def format_sentiment_score(score):
    """
    Format sentiment score for display.

    Args:
        score (float): Sentiment score

    Returns:
        str: Formatted string
    """
    return f"{score:.2f}"


