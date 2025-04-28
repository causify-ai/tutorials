"""
Module to set up logging.
"""

import logging


def setup(
    log_level: int = logging.INFO,
    log_file: str = "default_btc_rl_agent.log",
    enable_console: bool = True,
    enable_file: bool = True,
):
    """
    Sets up the logger.

    This function configures the logger with customizable handlers for console and file output.
    Supports all standard logging levels: DEBUG, INFO, WARN, ERROR, and CRITICAL.

    :param log_level: The minimum logging level (DEBUG, INFO, WARN, ERROR, CRITICAL). Defaults to INFO
    :param log_file: The file to which logs will be written. Defaults to 'bitcoin_rl_agent.log'
    :param enable_console: Whether to enable console logging. Defaults to True
    :param enable_file: Whether to enable file logging. Defaults to True
    :return: The logger instance
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    # Clear any existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    # Define log format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # Create and add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    # Create and add file handler if enabled
    if enable_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    # Ensure logs propagate up to the root logger
    logger.propagate = True
    return logger
