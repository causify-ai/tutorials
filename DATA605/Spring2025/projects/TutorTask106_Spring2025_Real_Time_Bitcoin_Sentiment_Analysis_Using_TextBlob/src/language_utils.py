"""
language_utils.py

This file contains utility functions for language detection, translation,
and multi-language sentiment analysis support.
"""

from textblob import TextBlob
from googletrans import Translator
import logging
from deep_translator import GoogleTranslator

from src.logger import get_logger
import asyncio
from functools import wraps
from langdetect import detect, LangDetectException

logger = get_logger(__name__)

# Supported languages and their codes
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'nl': 'Dutch',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese'
}

# def run_async(coro):
#     """Helper function to run coroutines in synchronous context."""
#     try:
#         loop = asyncio.get_event_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#     return loop.run_until_complete(coro)

def detect_language(text: str) -> str:
    """
    Detect the language of the given text.

    Args:
        text (str): Text to analyze

    Returns:
        str: ISO 639-1 language code (e.g., 'en', 'es', etc.)
    """
    if not isinstance(text, str) or not text.strip():
        return 'en'
    try:
        return detect(text)
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}")
        return 'en'


def translate_text(text: str, target_language: str = 'en') -> str:
    """
    Translate text to the target language using deep-translator's GoogleTranslator.

    Args:
        text (str): Text to translate
        target_language (str): ISO 639-1 target language code (default: 'en')

    Returns:
        str: Translated text (or original text on failure/empty input)
    """
    if not isinstance(text, str) or not text.strip():
        return text
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        return translator.translate(text)
    except Exception as e:
        logger.warning(f"Error translating text: {e}")
        return text



def analyze_multilingual_sentiment(text):
    """
    Analyze sentiment of text in any supported language.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        tuple: (polarity, subjectivity, original_language)
    """
    if not isinstance(text, str) or not text.strip():
        return 0.0, 0.0, 'en'
    
    try:
        # Detect language
        original_lang = detect_language(text)
        
        # Translate to English if needed
        if original_lang != 'en':
            text = translate_text(text, 'en')
        
        # Perform sentiment analysis
        blob = TextBlob(text)
        return blob.sentiment.polarity, blob.sentiment.subjectivity, original_lang
    except Exception as e:
        logger.warning(f"Error in multilingual sentiment analysis: {e}")
        return 0.0, 0.0, 'en' 