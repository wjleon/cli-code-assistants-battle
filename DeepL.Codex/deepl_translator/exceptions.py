"""Custom exceptions for DeepL translator integration."""

class DeepLException(Exception):
    """Base exception for DeepL related errors."""
    pass

class MissingAPIKeyException(DeepLException):
    """Raised when the DeepL API key is missing."""
    pass