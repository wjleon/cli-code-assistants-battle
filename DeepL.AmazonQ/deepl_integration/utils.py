"""
Utility functions for the DeepL API integration.

This module provides utility functions for common tasks such as environment variable
handling, request preparation, and response parsing.
"""

import os
import logging
from typing import Optional, Dict, Any

from .exceptions import AuthenticationError

# Configure logging
logger = logging.getLogger(__name__)


def get_api_key() -> str:
    """
    Get the DeepL API key from the environment variables.

    Returns:
        The DeepL API key.

    Raises:
        AuthenticationError: If the API key is not set in the environment variables.
    """
    api_key = os.environ.get('DEEPL_API_KEY')
    if not api_key:
        logger.error("DEEPL_API_KEY environment variable not set")
        raise AuthenticationError("DEEPL_API_KEY environment variable not set")
    return api_key


def clean_text(text: str) -> str:
    """
    Clean and prepare text for translation.

    Args:
        text: The text to clean.

    Returns:
        The cleaned text.
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    cleaned = ' '.join(text.split())
    return cleaned


def map_error_code(status_code: int, response_json: Optional[Dict[str, Any]] = None) -> str:
    """
    Map HTTP status codes to human-readable error messages.

    Args:
        status_code: The HTTP status code.
        response_json: Optional JSON response from the API.

    Returns:
        A human-readable error message.
    """
    error_messages = {
        400: "Bad request: The request was invalid",
        401: "Authentication failed: Invalid API key",
        403: "Forbidden: Access denied",
        404: "Not found: The requested resource was not found",
        413: "Payload too large: The request size exceeds the limit",
        429: "Too many requests: Rate limit or quota exceeded",
        456: "Quota exceeded: The character limit has been reached",
        500: "Internal server error: Something went wrong on DeepL's end",
        503: "Service unavailable: DeepL service is temporarily unavailable"
    }
    
    # Get error message from response if available
    message = None
    if response_json and 'message' in response_json:
        message = response_json['message']
    
    # Use default message if no specific message is available
    if not message:
        message = error_messages.get(status_code, f"Unknown error: HTTP {status_code}")
    
    return message
