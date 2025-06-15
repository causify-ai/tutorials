# util.py

import logging
import pandas as pd
from typing import List, Dict, Optional


def setup_logging(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger instance.

    :param name: Name for the logger.
    :param level: Logging level.
    :return: Configured logger.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


def format_timestamp(ts: pd.Timestamp) -> str:
    """
    Format pandas Timestamp to a human-readable string.

    :param ts: pandas Timestamp object.
    :return: Formatted string.
    """
    return ts.strftime('%Y-%m-%d %H:%M:%S')


def save_data_to_csv(data: List[Dict], filepath: str) -> None:
    """
    Save collected data to a CSV file.

    :param data: List of dictionaries with data entries.
    :param filepath: Path to the output CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)


def handle_api_error(e: Exception, logger: logging.Logger) -> None:
    """
    Handle and log API errors.

    :param e: Exception object.
    :param logger: Logger to log the error.
    """
    logger.warning("Error during API request: %s", str(e))


def validate_price_response(response_json: dict) -> Optional[float]:
    """
    Extract Bitcoin price from CoinGecko API JSON response.

    :param response_json: JSON object returned by the API.
    :return: Bitcoin price or None.
    """
    try:
        return response_json['bitcoin']['usd']
    except KeyError:
        return None
