import logging

def setup_logging():
    """Set up logging configuration"""
    logger = logging.getLogger('bitcoin_fetcher')
    
    # Clear existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers = []
        
    logger.setLevel(logging.INFO)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(ch)
    
    return logger