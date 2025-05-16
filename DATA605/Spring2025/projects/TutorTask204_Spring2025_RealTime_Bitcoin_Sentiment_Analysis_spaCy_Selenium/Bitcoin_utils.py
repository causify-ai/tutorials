"""
Additional utility functions for the Bitcoin sentiment analysis project.
"""
import logging

# Set up logger
_LOG = logging.getLogger(__name__)

def log_message(message: str) -> None:
    """
    Log a message with INFO level.

    :param message: The message to log.
    :return: None
    """
    _LOG.info(message)