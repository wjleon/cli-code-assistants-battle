"""
Custom exceptions for the DeepL API integration.

This module defines custom exceptions that provide clear and specific error messages
for different types of failures that can occur when interacting with the DeepL API.
"""

class DeepLError(Exception):
    """Base exception for all DeepL API related errors."""
    pass


class AuthenticationError(DeepLError):
    """Raised when authentication with the DeepL API fails."""
    pass


class QuotaExceededError(DeepLError):
    """Raised when the DeepL API quota has been exceeded."""
    pass


class ValidationError(DeepLError):
    """Raised when the request parameters are invalid."""
    pass


class RateLimitError(DeepLError):
    """Raised when the DeepL API rate limit has been exceeded."""
    pass


class ServerError(DeepLError):
    """Raised when the DeepL API server encounters an error."""
    pass


class ConnectionError(DeepLError):
    """Raised when there is an issue connecting to the DeepL API."""
    pass


class TimeoutError(DeepLError):
    """Raised when a request to the DeepL API times out."""
    pass


class UnexpectedResponseError(DeepLError):
    """Raised when the DeepL API returns an unexpected response."""
    pass
