#!/usr/bin/env python3
"""
Unified configuration parser for Bitcoin Price Forecasting System.
This module provides functions to load and access the unified configuration.
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Default configuration paths
DEFAULT_CONFIG_PATH = '/app/configs/unified_config.yaml'
LOCAL_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs/unified_config.yaml')

# Global configuration cache
_config_cache = None

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from the specified path or use default paths.
    
    Args:
        config_path: Optional path to the configuration file.
                    If None, will try default paths.
    
    Returns:
        Dict containing the configuration.
    
    Raises:
        FileNotFoundError: If no configuration file can be found.
    """
    global _config_cache
    
    # Return cached config if available
    if _config_cache is not None:
        return _config_cache
    
    # Try the provided path first
    if config_path and os.path.exists(config_path):
        config_file = config_path
    # Try the default Docker path
    elif os.path.exists(DEFAULT_CONFIG_PATH):
        config_file = DEFAULT_CONFIG_PATH
    # Try the local development path
    elif os.path.exists(LOCAL_CONFIG_PATH):
        config_file = LOCAL_CONFIG_PATH
    else:
        raise FileNotFoundError(f"Configuration file not found at {config_path}, {DEFAULT_CONFIG_PATH}, or {LOCAL_CONFIG_PATH}")
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_file}")
        _config_cache = config
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise

def get_service_config(service_name: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get configuration for a specific service.
    
    Args:
        service_name: Name of the service (e.g., 'data_collector', 'dashboard')
        config_path: Optional path to the configuration file.
    
    Returns:
        Dict containing the service-specific configuration merged with global settings.
    """
    config = load_config(config_path)
    
    # Start with a copy of the global configuration
    service_config = {
        'app': config.get('app', {}),
        'data': config.get('data', {}),
        'data_format': config.get('data_format', {}),
        'kafka': config.get('kafka', {})
    }
    
    # Add service-specific configuration if available
    if 'services' in config and service_name in config['services']:
        # Copy the service-specific config to the top level
        service_specific = config['services'][service_name]
        service_config[service_name] = service_specific
        
        # Also add model config to top level for backward compatibility
        if 'model' in service_specific:
            service_config['model'] = service_specific['model']
    else:
        # Check if service config is directly at top level (old format)
        if service_name in config:
            service_config[service_name] = config[service_name]
            # Also add model config if available
            if 'model' in config[service_name]:
                service_config['model'] = config[service_name]['model']
        else:
            logger.warning(f"No specific configuration found for service '{service_name}'")
            service_config[service_name] = {}
    
    # Add global model config if available and not already set
    if 'model' in config and 'model' not in service_config:
        service_config['model'] = config['model']
    
    # Debug log the final config structure
    logger.debug(f"Final service config keys: {list(service_config.keys())}")
    if 'model' in service_config:
        logger.debug(f"Model config available at top level")
    if service_name in service_config and 'model' in service_config[service_name]:
        logger.debug(f"Model config available in service-specific section")
    
    return service_config

def get_global_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get global configuration settings.
    
    Args:
        config_path: Optional path to the configuration file.
    
    Returns:
        Dict containing the global configuration settings.
    """
    config = load_config(config_path)
    
    # Extract global configuration sections
    global_config = {
        'app': config.get('app', {}),
        'data': config.get('data', {}),
        'data_format': config.get('data_format', {}),
        'kafka': config.get('kafka', {})
    }
    
    return global_config

def get_config_value(key_path: str, default=None, config_path: Optional[str] = None) -> Any:
    """
    Get a specific configuration value using dot notation.
    
    Args:
        key_path: Path to the config value using dot notation (e.g., 'kafka.topic')
        default: Default value to return if the key is not found
        config_path: Optional path to the configuration file.
    
    Returns:
        The configuration value or the default if not found.
    """
    config = load_config(config_path)
    
    # Split the key path and traverse the config dictionary
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value

def reload_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Force reload of the configuration from disk.
    
    Args:
        config_path: Optional path to the configuration file.
    
    Returns:
        Dict containing the reloaded configuration.
    """
    global _config_cache
    _config_cache = None
    return load_config(config_path) 