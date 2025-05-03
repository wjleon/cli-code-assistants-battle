"""
Utility functions for DeepL API integration.

This module provides helper functions for resource management, retry mechanisms,
and other utilities used throughout the DeepL API client.
"""

import time
import logging
import random
import functools
import contextlib
from typing import TypeVar, Callable, Any, Optional, Dict, List, Union, Type, cast
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.exceptions import (
    DeepLError,
    ConnectionError,
    TimeoutError,
    RateLimitError,
    ServerError,
    TooManyRequestsError,
)

# Setup logging
logger = logging.getLogger("deepl_integration")

# Type variable for generic function return type
T = TypeVar("T")


def create_retry_session(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: Optional[List[int]] = None,
    allowed_methods: Optional[List[str]] = None,
) -> requests.Session:
    """
    Create a requests Session with retry capabilities.
    
    Args:
        retries: Maximum number of retries.
        backoff_factor: Backoff factor for retry delay calculation.
        status_forcelist: HTTP status codes that should trigger a retry.
        allowed_methods: HTTP methods that should be retried.
        
    Returns:
        A requests Session configured with retry capabilities.
    """
    if status_forcelist is None:
        status_forcelist = [429, 500, 502, 503, 504]
    
    if allowed_methods is None:
        allowed_methods = ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
    
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
    )
    
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


@contextlib.contextmanager
def managed_session(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: Optional[List[int]] = None,
    allowed_methods: Optional[List[str]] = None,
) -> requests.Session:
    """
    Context manager for a requests Session with retry capabilities.
    
    This ensures that the session is properly closed when it's no longer needed,
    preventing resource leaks.
    
    Args:
        retries: Maximum number of retries.
        backoff_factor: Backoff factor for retry delay calculation.
        status_forcelist: HTTP status codes that should trigger a retry.
        allowed_methods: HTTP methods that should be retried.
        
    Yields:
        A requests Session configured with retry capabilities.
    """
    session = create_retry_session(
        retries=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
    )
    
    try:
        yield session
    finally:
        session.close()


def retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retry_on_exceptions: Optional[List[Type[Exception]]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry decorator for functions that might fail temporarily.
    
    Args:
        max_retries: Maximum number of retries.
        initial_delay: Initial delay between retries in seconds.
        max_delay: Maximum delay between retries in seconds.
        backoff_factor: Factor by which the delay increases with each retry.
        jitter: Whether to add random jitter to the delay.
        retry_on_exceptions: List of exceptions that should trigger a retry.
        
    Returns:
        A decorator function.
    """
    if retry_on_exceptions is None:
        retry_on_exceptions = [
            ConnectionError,
            TimeoutError,
            RateLimitError,
            ServerError,
            TooManyRequestsError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ReadTimeout,
        ]
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            delay = initial_delay
            
            for retry_count in range(max_retries + 1):
                try:
                    if retry_count > 0:
                        logger.debug(
                            f"Retry {retry_count}/{max_retries} for {func.__name__} "
                            f"after {delay:.2f}s delay"
                        )
                        time.sleep(delay)
                        
                        # Update delay for next retry with exponential backoff
                        delay = min(delay * backoff_factor, max_delay)
                        
                        # Add jitter if enabled
                        if jitter:
                            delay = delay * (0.5 + random.random())
                    
                    return func(*args, **kwargs)
                
                except tuple(retry_on_exceptions) as e:
                    last_exception = e
                    
                    # Don't retry if we've reached the maximum number of retries
                    if retry_count >= max_retries:
                        break
                    
                    # Special handling for rate limit errors
                    if isinstance(e, RateLimitError) or isinstance(e, TooManyRequestsError):
                        # Use a longer delay for rate limit errors
                        delay = min(delay * 2, max_delay)
            
            # If we've exhausted all retries, raise the last exception
            if last_exception is not None:
                logger.error(
                    f"Failed after {max_retries} retries: {func.__name__} - "
                    f"{type(last_exception).__name__}: {str(last_exception)}"
                )
                raise last_exception
            
            # This should never happen, but mypy needs it
            raise RuntimeError("Unexpected error in retry decorator")
        
        return cast(Callable[..., T], wrapper)
    
    return decorator


def safe_request(
    session: requests.Session,
    method: str,
    url: str,
    timeout: int = 10,
    **kwargs: Any,
) -> requests.Response:
    """
    Make a safe HTTP request with proper error handling.
    
    Args:
        session: The requests Session to use.
        method: The HTTP method to use.
        url: The URL to request.
        timeout: Request timeout in seconds.
        **kwargs: Additional arguments to pass to the request method.
        
    Returns:
        The HTTP response.
        
    Raises:
        DeepLError: If the request fails.
    """
    try:
        response = session.request(method, url, timeout=timeout, **kwargs)
        return response
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timed out: {url}")
        raise TimeoutError(f"Request timed out: {str(e)}") from e
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {url}")
        raise ConnectionError(f"Connection error: {str(e)}") from e
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {url} - {str(e)}")
        raise DeepLError(f"Request error: {str(e)}") from e


def chunk_text(text: str, max_chunk_size: int = 5000) -> List[str]:
    """
    Split a long text into smaller chunks for processing.
    
    This is useful for handling large texts that might exceed API limits.
    The function tries to split at sentence boundaries when possible.
    
    Args:
        text: The text to split.
        max_chunk_size: Maximum size of each chunk in characters.
        
    Returns:
        A list of text chunks.
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Common sentence-ending punctuation
    sentence_endings = [". ", "! ", "? ", ".\n", "!\n", "?\n"]
    
    # Split by newlines first to preserve paragraph structure
    paragraphs = text.split("\n")
    
    for paragraph in paragraphs:
        if not paragraph:
            # Handle empty paragraphs
            if current_chunk and len(current_chunk) + 1 <= max_chunk_size:
                current_chunk += "\n"
            continue
        
        if len(paragraph) <= max_chunk_size:
            # If the paragraph fits in a chunk with the current content, add it
            if len(current_chunk) + len(paragraph) + 1 <= max_chunk_size:
                if current_chunk:
                    current_chunk += "\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                # Otherwise, start a new chunk
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph
        else:
            # If the paragraph is too large, we need to split it
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            
            # Try to split at sentence boundaries
            sentences = []
            last_end = 0
            
            for i in range(len(paragraph)):
                # Check if we're at a sentence ending
                for ending in sentence_endings:
                    if i + len(ending) <= len(paragraph) and paragraph[i:i+len(ending)] == ending:
                        sentences.append(paragraph[last_end:i+1])
                        last_end = i + 1
                        break
            
            # Add the last sentence if there's any remaining text
            if last_end < len(paragraph):
                sentences.append(paragraph[last_end:])
            
            # Combine sentences into chunks
            for sentence in sentences:
                if not current_chunk:
                    current_chunk = sentence
                elif len(current_chunk) + len(sentence) <= max_chunk_size:
                    current_chunk += sentence
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence
    
    # Add the last chunk if there's any remaining text
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def merge_translated_chunks(chunks: List[str]) -> str:
    """
    Merge translated text chunks back into a single text.
    
    Args:
        chunks: List of translated text chunks.
        
    Returns:
        The merged text.
    """
    return "".join(chunks)


def format_glossary_entries(
    entries: Dict[str, str],
    format_type: str = "csv",
) -> str:
    """
    Format glossary entries according to the specified format.
    
    Args:
        entries: Dictionary of source terms (keys) and target terms (values).
        format_type: Format type, either 'csv' or 'tsv'.
        
    Returns:
        Formatted glossary entries as a string.
        
    Raises:
        ValueError: If an unsupported format type is specified.
    """
    if format_type.lower() not in ["csv", "tsv"]:
        raise ValueError(f"Unsupported glossary format: {format_type}")
    
    separator = "," if format_type.lower() == "csv" else "\t"
    lines = []
    
    for source, target in entries.items():
        # Escape quotes in CSV format
        if format_type.lower() == "csv":
            source = source.replace('"', '""')
            target = target.replace('"', '""')
            line = f'"{source}"{separator}"{target}"'
        else:
            line = f"{source}{separator}{target}"
        
        lines.append(line)
    
    return "\n".join(lines)


def parse_glossary_entries(
    content: str,
    format_type: str = "csv",
) -> Dict[str, str]:
    """
    Parse glossary entries from a string.
    
    Args:
        content: String containing glossary entries.
        format_type: Format type, either 'csv' or 'tsv'.
        
    Returns:
        Dictionary of source terms (keys) and target terms (values).
        
    Raises:
        ValueError: If an unsupported format type is specified or if the content is invalid.
    """
    if format_type.lower() not in ["csv", "tsv"]:
        raise ValueError(f"Unsupported glossary format: {format_type}")
    
    separator = "," if format_type.lower() == "csv" else "\t"
    entries = {}
    
    for line in content.strip().split("\n"):
        if not line.strip():
            continue
        
        parts = line.split(separator)
        if len(parts) != 2:
            raise ValueError(f"Invalid glossary entry: {line}")
        
        source = parts[0].strip()
        target = parts[1].strip()
        
        # Remove quotes in CSV format
        if format_type.lower() == "csv":
            if source.startswith('"') and source.endswith('"'):
                source = source[1:-1].replace('""', '"')
            if target.startswith('"') and target.endswith('"'):
                target = target[1:-1].replace('""', '"')
        
        entries[source] = target
    
    return entries


def clean_memory_resources() -> None:
    """
    Clean up memory resources to prevent memory leaks.
    
    This function can be called periodically to help manage memory usage.
    """
    # Force garbage collection
    import gc
    gc.collect()


def sanitize_api_key(api_key: str) -> str:
    """
    Sanitize the API key for logging purposes.
    
    Args:
        api_key: The API key to sanitize.
        
    Returns:
        A sanitized version of the API key (first 4 chars + ***).
    """
    if not api_key:
        return ""
    
    if len(api_key) <= 8:
        return "****"
    
    return api_key[:4] + "****" + api_key[-4:]


def validate_file_size(file_path: str, max_size_mb: float = 50.0) -> bool:
    """
    Validate that a file does not exceed the maximum size.
    
    Args:
        file_path: Path to the file.
        max_size_mb: Maximum file size in megabytes.
        
    Returns:
        True if the file size is valid, False otherwise.
    """
    import os
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    return file_size_mb <= max_size_mb


def get_file_mime_type(file_path: str) -> str:
    """
    Get the MIME type of a file.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        The MIME type of the file.
        
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    import os
    import mimetypes
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if mime_type is None:
        # Default to application/octet-stream if the MIME type cannot be determined
        return "application/octet-stream"
    
    return mime_type
