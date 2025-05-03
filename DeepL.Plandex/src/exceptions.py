"""
Custom exceptions for DeepL API integration.

This module defines a hierarchy of custom exceptions for different error scenarios
that may occur when interacting with the DeepL API.
"""

from typing import Optional, Dict, Any


class DeepLError(Exception):
    """Base exception class for all DeepL API related errors."""
    
    def __init__(self, message: str = "An error occurred with the DeepL API."):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(DeepLError):
    """Exception raised for authentication errors with the DeepL API."""
    
    def __init__(self, message: str = "Authentication failed with the DeepL API. Please check your API key."):
        self.message = message
        super().__init__(self.message)


class QuotaExceededError(DeepLError):
    """Exception raised when the DeepL API quota has been exceeded."""
    
    def __init__(self, message: str = "DeepL API quota exceeded. Please check your usage limits."):
        self.message = message
        super().__init__(self.message)


class RateLimitError(DeepLError):
    """Exception raised when the DeepL API rate limit has been reached."""
    
    def __init__(self, message: str = "DeepL API rate limit reached. Please try again later."):
        self.message = message
        super().__init__(self.message)


class InvalidRequestError(DeepLError):
    """Exception raised for invalid requests to the DeepL API."""
    
    def __init__(self, message: str = "Invalid request to the DeepL API."):
        self.message = message
        super().__init__(self.message)


class UnsupportedLanguageError(InvalidRequestError):
    """Exception raised when an unsupported language is requested."""
    
    def __init__(self, language_code: str = "", message: Optional[str] = None):
        if message is None:
            message = f"Unsupported language: {language_code}" if language_code else "Unsupported language."
        self.language_code = language_code
        super().__init__(message)


class TextTooLargeError(InvalidRequestError):
    """Exception raised when the text to translate is too large."""
    
    def __init__(self, message: str = "The text to translate is too large. Please reduce the size."):
        super().__init__(message)


class DocumentTooLargeError(InvalidRequestError):
    """Exception raised when the document to translate is too large."""
    
    def __init__(self, message: str = "The document to translate is too large. Please reduce the size."):
        super().__init__(message)


class TooManyRequestsError(DeepLError):
    """Exception raised when too many requests are made to the DeepL API."""
    
    def __init__(self, message: str = "Too many requests to the DeepL API. Please try again later."):
        self.message = message
        super().__init__(self.message)


class ServerError(DeepLError):
    """Exception raised for server-side errors from the DeepL API."""
    
    def __init__(self, message: str = "DeepL API server error. Please try again later."):
        self.message = message
        super().__init__(self.message)


class ConnectionError(DeepLError):
    """Exception raised for connection errors with the DeepL API."""
    
    def __init__(self, message: str = "Connection error with the DeepL API. Please check your internet connection."):
        self.message = message
        super().__init__(self.message)


class TimeoutError(DeepLError):
    """Exception raised when a request to the DeepL API times out."""
    
    def __init__(self, message: str = "Request to the DeepL API timed out. Please try again later."):
        self.message = message
        super().__init__(self.message)


class ResourceNotFoundError(DeepLError):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, resource_id: str = "", message: Optional[str] = None):
        if message is None:
            message = f"Resource not found: {resource_id}" if resource_id else "Resource not found."
        self.resource_id = resource_id
        super().__init__(message)


class GlossaryError(DeepLError):
    """Base exception for glossary-related errors."""
    
    def __init__(self, message: str = "An error occurred with the DeepL glossary."):
        self.message = message
        super().__init__(self.message)


class GlossaryNotFoundError(GlossaryError):
    """Exception raised when a glossary is not found."""
    
    def __init__(self, glossary_id: str = "", message: Optional[str] = None):
        if message is None:
            message = f"Glossary not found: {glossary_id}" if glossary_id else "Glossary not found."
        self.glossary_id = glossary_id
        super().__init__(message)


class GlossaryLimitExceededError(GlossaryError):
    """Exception raised when the glossary limit has been exceeded."""
    
    def __init__(self, message: str = "Glossary limit exceeded. Please delete some glossaries."):
        super().__init__(message)


class DocumentTranslationError(DeepLError):
    """Base exception for document translation errors."""
    
    def __init__(self, message: str = "An error occurred during document translation."):
        self.message = message
        super().__init__(self.message)


class DocumentUploadError(DocumentTranslationError):
    """Exception raised when a document upload fails."""
    
    def __init__(self, message: str = "Failed to upload document for translation."):
        super().__init__(message)


class DocumentDownloadError(DocumentTranslationError):
    """Exception raised when a document download fails."""
    
    def __init__(self, message: str = "Failed to download translated document."):
        super().__init__(message)


class DocumentTranslationTimeoutError(DocumentTranslationError):
    """Exception raised when a document translation times out."""
    
    def __init__(self, message: str = "Document translation timed out. Please try again later."):
        super().__init__(message)


def map_http_error_to_exception(status_code: int, response_data: Optional[Dict[str, Any]] = None) -> DeepLError:
    """
    Map an HTTP error status code to the appropriate exception.
    
    Args:
        status_code: The HTTP status code.
        response_data: Optional response data from the API.
        
    Returns:
        An instance of the appropriate DeepLError subclass.
    """
    error_message = "Unknown error"
    if response_data and "message" in response_data:
        error_message = response_data["message"]
    
    if status_code == 401:
        return AuthenticationError(error_message)
    elif status_code == 403:
        if "quota" in error_message.lower():
            return QuotaExceededError(error_message)
        return AuthenticationError(error_message)
    elif status_code == 404:
        if "glossary" in error_message.lower():
            glossary_id = response_data.get("glossary_id", "") if response_data else ""
            return GlossaryNotFoundError(glossary_id, error_message)
        return ResourceNotFoundError("", error_message)
    elif status_code == 413:
        if "document" in error_message.lower():
            return DocumentTooLargeError(error_message)
        return TextTooLargeError(error_message)
    elif status_code == 429:
        if "rate" in error_message.lower():
            return RateLimitError(error_message)
        return TooManyRequestsError(error_message)
    elif status_code == 456:
        return QuotaExceededError(error_message)
    elif status_code == 503:
        return ServerError(error_message)
    elif 400 <= status_code < 500:
        if "language" in error_message.lower():
            language_code = ""
            if response_data and "language" in response_data:
                language_code = response_data["language"]
            return UnsupportedLanguageError(language_code, error_message)
        return InvalidRequestError(error_message)
    elif 500 <= status_code < 600:
        return ServerError(error_message)
    
    return DeepLError(error_message)
