"""
Configuration module for DeepL API integration.

This module handles the retrieval and validation of the DeepL API key
from environment variables.
"""

import os
import re
from typing import Optional


class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass


class APIKeyNotFoundError(ConfigError):
    """Exception raised when the API key is not found in environment variables."""
    
    def __init__(self, message: str = "DeepL API key not found in environment variables. "
                                      "Please set the DEEPL_API_KEY environment variable."):
        self.message = message
        super().__init__(self.message)


class InvalidAPIKeyError(ConfigError):
    """Exception raised when the API key format is invalid."""
    
    def __init__(self, message: str = "Invalid DeepL API key format. "
                                      "Please check your API key and try again."):
        self.message = message
        super().__init__(self.message)


def get_api_key() -> str:
    """
    Retrieve the DeepL API key from environment variables.
    
    Returns:
        str: The DeepL API key.
        
    Raises:
        APIKeyNotFoundError: If the API key is not found in environment variables.
        InvalidAPIKeyError: If the API key format is invalid.
    """
    api_key = os.environ.get("DEEPL_API_KEY")
    
    if not api_key:
        raise APIKeyNotFoundError()
    
    if not _is_valid_api_key(api_key):
        raise InvalidAPIKeyError()
    
    return api_key


def _is_valid_api_key(api_key: str) -> bool:
    """
    Validate the format of the DeepL API key.
    
    DeepL API keys typically follow these formats:
    - Free API: 32 characters, starts with 'f' (e.g., f123456789012345678901234567890)
    - Pro API: 32 characters, starts with numbers or other characters
    
    Args:
        api_key (str): The API key to validate.
        
    Returns:
        bool: True if the API key format is valid, False otherwise.
    """
    # Basic validation: non-empty string with reasonable length
    if not api_key or len(api_key) < 32:
        return False
    
    # Check for common API key patterns
    # Free tier API keys typically start with 'f' followed by alphanumeric characters
    free_api_pattern = re.compile(r'^f[a-zA-Z0-9]{31,}$')
    # Pro tier API keys are typically alphanumeric
    pro_api_pattern = re.compile(r'^[a-zA-Z0-9]{32,}$')
    
    return bool(free_api_pattern.match(api_key) or pro_api_pattern.match(api_key))


def get_api_url(is_free_api: Optional[bool] = None) -> str:
    """
    Get the appropriate DeepL API URL based on the API key type.
    
    If is_free_api is not provided, it will be determined from the API key.
    
    Args:
        is_free_api (Optional[bool]): Whether to use the free API URL.
            If None, it will be determined from the API key.
            
    Returns:
        str: The DeepL API URL.
    """
    api_key = get_api_key()
    
    # Determine if using free API if not explicitly specified
    if is_free_api is None:
        is_free_api = api_key.startswith('f')
    
    if is_free_api:
        return "https://api-free.deepl.com/v2"
    else:
        return "https://api.deepl.com/v2"


def get_config():
    """
    Get the complete configuration for the DeepL API client.
    
    Returns:
        dict: A dictionary containing the configuration.
        
    Raises:
        APIKeyNotFoundError: If the API key is not found in environment variables.
        InvalidAPIKeyError: If the API key format is invalid.
    """
    api_key = get_api_key()
    is_free_api = api_key.startswith('f')
    
    return {
        "api_key": api_key,
        "api_url": get_api_url(is_free_api),
        "is_free_api": is_free_api,
        "timeout": int(os.environ.get("DEEPL_TIMEOUT", "10")),
        "max_retries": int(os.environ.get("DEEPL_MAX_RETRIES", "3")),
    }
