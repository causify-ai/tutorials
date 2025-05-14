import logging

def get_logger(name: str, log_level=None):
    """
    Get a logger with the specified name and log level.
    
    Args:
        name: Name of the logger
        log_level: Log level (e.g., 'INFO', 'DEBUG', etc.) or None to use default
        
    Returns:
        logging.Logger: Configured logger
    """
    # Set default log level to INFO if not specified
    if log_level is None:
        level = logging.INFO
    elif isinstance(log_level, str):
        # Convert string log level to logging constant
        level = getattr(logging, log_level.upper(), logging.INFO)
    else:
        # Use the provided level directly
        level = log_level
    
    # Configure root logger if not already configured
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)s | %(name)s.%(funcName)s() | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get the logger and set its level
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    return logger