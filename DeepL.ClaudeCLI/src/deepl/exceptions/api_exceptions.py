"""
Exceptions for the DeepL API client.
"""
from typing import Dict, Any, Optional


class DeepLAPIError(Exception):
    """Base exception for all DeepL API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        """
        Initialize a DeepL API error.

        Args:
            message: Error message
            status_code: HTTP status code
            response: Raw API response
        """
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class AuthorizationError(DeepLAPIError):
    """Exception raised when API key is invalid or authorization fails."""
    pass


class QuotaExceededError(DeepLAPIError):
    """Exception raised when the API quota or character limit is exceeded."""
    pass


class RequestError(DeepLAPIError):
    """Exception raised when a request to the API fails."""
    pass


class ConnectionError(DeepLAPIError):
    """Exception raised when there's a connection error to the API."""
    pass


class ValidationError(DeepLAPIError):
    """Exception raised when request validation fails."""
    pass


def handle_api_error(status_code: int, response_body: Dict[str, Any]) -> DeepLAPIError:
    """
    Factory method to create the appropriate exception based on the status code.

    Args:
        status_code: HTTP status code
        response_body: API response body

    Returns:
        An instance of the appropriate exception
    """
    error_message = response_body.get('message', 'Unknown error')
    
    if status_code == 401 or status_code == 403:
        return AuthorizationError(f"Authentication error: {error_message}", status_code, response_body)
    elif status_code == 429 or status_code == 456:
        return QuotaExceededError(f"Quota exceeded: {error_message}", status_code, response_body)
    elif status_code == 400:
        return ValidationError(f"Validation error: {error_message}", status_code, response_body)
    else:
        return RequestError(f"API request error: {error_message}", status_code, response_body)