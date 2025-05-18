import os
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(name, log_level=None, log_file=None):
    """
    Configure logging for the application.
    
    Args:
        name: Logger name
        log_level: Logging level (default: from environment or INFO)
        log_file: Log file path (default: from environment or None)
    
    Returns:
        Logger instance
    """
    # Get log level from environment if not specified
    if log_level is None:
        log_level_str = os.environ.get('LOG_LEVEL', 'INFO')
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Get log file from environment if not specified
    if log_file is None:
        log_file = os.environ.get('LOG_FILE')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers = []
    
    # Always add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Create rotating file handler (10MB max, keep 5 backup files)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 