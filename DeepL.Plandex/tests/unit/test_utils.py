"""
Unit tests for the utils module.
"""

import os
import time
import pytest
import tempfile
from unittest.mock import patch, MagicMock, call

import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout as RequestsTimeout

from src.utils import (
    create_retry_session,
    managed_session,
    retry,
    safe_request,
    chunk_text,
    merge_translated_chunks,
    format_glossary_entries,
    parse_glossary_entries,
    clean_memory_resources,
    sanitize_api_key,
    validate_file_size,
    get_file_mime_type,
)
from src.exceptions import (
    ConnectionError,
    TimeoutError,
    RateLimitError,
    ServerError,
    TooManyRequestsError,
    DeepLError,
)


class TestRetrySession:
    """Tests for the retry session functionality."""

    def test_create_retry_session(self):
        """Test that create_retry_session returns a requests.Session."""
        session = create_retry_session()
        assert isinstance(session, requests.Session)

    def test_create_retry_session_with_custom_parameters(self):
        """Test that create_retry_session accepts custom parameters."""
        session = create_retry_session(
            retries=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502],
            allowed_methods=["GET", "POST"],
        )
        assert isinstance(session, requests.Session)

    def test_managed_session(self):
        """Test that managed_session returns a context manager for a requests.Session."""
        with managed_session() as session:
            assert isinstance(session, requests.Session)

    def test_managed_session_closes_session(self):
        """Test that managed_session closes the session when exiting the context."""
        with patch("requests.Session.close") as mock_close:
            with managed_session():
                pass
            mock_close.assert_called_once()


class TestRetryDecorator:
    """Tests for the retry decorator."""

    def test_retry_success_first_attempt(self):
        """Test that a function that succeeds on the first attempt is not retried."""
        mock_func = MagicMock(return_value="success")
        decorated_func = retry()(mock_func)
        
        result = decorated_func()
        
        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_success_after_retries(self):
        """Test that a function that succeeds after retries returns the correct result."""
        mock_func = MagicMock(side_effect=[ConnectionError(), ConnectionError(), "success"])
        decorated_func = retry(max_retries=3, initial_delay=0.01)(mock_func)
        
        result = decorated_func()
        
        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_max_retries_exceeded(self):
        """Test that a function that always fails raises the last exception after max retries."""
        mock_func = MagicMock(side_effect=ConnectionError("Connection failed"))
        decorated_func = retry(max_retries=2, initial_delay=0.01)(mock_func)
        
        with pytest.raises(ConnectionError, match="Connection failed"):
            decorated_func()
        
        assert mock_func.call_count == 3  # Initial attempt + 2 retries

    def test_retry_with_different_exceptions(self):
        """Test that a function that raises different exceptions is retried correctly."""
        mock_func = MagicMock(side_effect=[
            ConnectionError("Connection failed"),
            TimeoutError("Timeout"),
            "success"
        ])
        decorated_func = retry(max_retries=3, initial_delay=0.01)(mock_func)
        
        result = decorated_func()
        
        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_with_non_retryable_exception(self):
        """Test that a function that raises a non-retryable exception is not retried."""
        mock_func = MagicMock(side_effect=ValueError("Invalid value"))
        decorated_func = retry(
            max_retries=3,
            initial_delay=0.01,
            retry_on_exceptions=[ConnectionError, TimeoutError]
        )(mock_func)
        
        with pytest.raises(ValueError, match="Invalid value"):
            decorated_func()
        
        assert mock_func.call_count == 1

    def test_retry_with_custom_retry_on_exceptions(self):
        """Test that a function that raises a custom exception is retried correctly."""
        mock_func = MagicMock(side_effect=[ValueError("Retry me"), "success"])
        decorated_func = retry(
            max_retries=3,
            initial_delay=0.01,
            retry_on_exceptions=[ValueError]
        )(mock_func)
        
        result = decorated_func()
        
        assert result == "success"
        assert mock_func.call_count == 2


class TestSafeRequest:
    """Tests for the safe_request function."""

    def test_safe_request_success(self):
        """Test that safe_request returns the response when the request succeeds."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_session.request.return_value = mock_response
        
        response = safe_request(mock_session, "GET", "https://example.com")
        
        assert response == mock_response
        mock_session.request.assert_called_once_with(
            "GET", "https://example.com", timeout=10
        )

    def test_safe_request_timeout(self):
        """Test that safe_request raises TimeoutError when the request times out."""
        mock_session = MagicMock()
        mock_session.request.side_effect = RequestsTimeout("Request timed out")
        
        with pytest.raises(TimeoutError):
            safe_request(mock_session, "GET", "https://example.com")

    def test_safe_request_connection_error(self):
        """Test that safe_request raises ConnectionError when the request fails with a connection error."""
        mock_session = MagicMock()
        mock_session.request.side_effect = RequestsConnectionError("Connection failed")
        
        with pytest.raises(ConnectionError):
            safe_request(mock_session, "GET", "https://example.com")

    def test_safe_request_other_exception(self):
        """Test that safe_request raises DeepLError when the request fails with another exception."""
        mock_session = MagicMock()
        mock_session.request.side_effect = requests.exceptions.RequestException("Request failed")
        
        with pytest.raises(DeepLError):
            safe_request(mock_session, "GET", "https://example.com")

    def test_safe_request_with_custom_timeout(self):
        """Test that safe_request uses the custom timeout when provided."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_session.request.return_value = mock_response
        
        response = safe_request(mock_session, "GET", "https://example.com", timeout=20)
        
        assert response == mock_response
        mock_session.request.assert_called_once_with(
            "GET", "https://example.com", timeout=20
        )

    def test_safe_request_with_additional_kwargs(self):
        """Test that safe_request passes additional kwargs to the request method."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_session.request.return_value = mock_response
        
        response = safe_request(
            mock_session,
            "POST",
            "https://example.com",
            json={"key": "value"},
            headers={"Content-Type": "application/json"},
        )
        
        assert response == mock_response
        mock_session.request.assert_called_once_with(
            "POST",
            "https://example.com",
            timeout=10,
            json={"key": "value"},
            headers={"Content-Type": "application/json"},
        )


class TestTextChunking:
    """Tests for the text chunking functionality."""

    def test_chunk_text_small_text(self):
        """Test that chunk_text returns a single chunk for small text."""
        text = "Hello, world!"
        chunks = chunk_text(text, max_chunk_size=100)
        assert chunks == ["Hello, world!"]

    def test_chunk_text_large_text(self):
        """Test that chunk_text splits large text into chunks."""
        text = "a" * 10000
        chunks = chunk_text(text, max_chunk_size=5000)
        assert len(chunks) == 2
        assert len(chunks[0]) <= 5000
        assert len(chunks[1]) <= 5000

    def test_chunk_text_with_sentences(self):
        """Test that chunk_text splits text at sentence boundaries when possible."""
        text = "Sentence one. Sentence two. Sentence three."
        chunks = chunk_text(text, max_chunk_size=20)
        assert len(chunks) == 2
        assert chunks[0] == "Sentence one."
        assert chunks[1] == " Sentence two. Sentence three."

    def test_chunk_text_with_paragraphs(self):
        """Test that chunk_text preserves paragraph structure when possible."""
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        chunks = chunk_text(text, max_chunk_size=30)
        assert len(chunks) == 2
        assert chunks[0] == "Paragraph one.\n\nParagraph two."
        assert chunks[1] == "\n\nParagraph three."

    def test_merge_translated_chunks(self):
        """Test that merge_translated_chunks combines chunks correctly."""
        chunks = ["Chunk one.", "Chunk two.", "Chunk three."]
        merged = merge_translated_chunks(chunks)
        assert merged == "Chunk one.Chunk two.Chunk three."


class TestGlossaryFormatting:
    """Tests for the glossary formatting functionality."""

    def test_format_glossary_entries_csv(self):
        """Test that format_glossary_entries formats entries correctly in CSV format."""
        entries = {"hello": "hallo", "world": "welt"}
        formatted = format_glossary_entries(entries, format_type="csv")
        assert formatted == '"hello","hallo"\n"world","welt"'

    def test_format_glossary_entries_tsv(self):
        """Test that format_glossary_entries formats entries correctly in TSV format."""
        entries = {"hello": "hallo", "world": "welt"}
        formatted = format_glossary_entries(entries, format_type="tsv")
        assert formatted == "hello\thallo\nworld\twelt"

    def test_format_glossary_entries_with_quotes_csv(self):
        """Test that format_glossary_entries escapes quotes in CSV format."""
        entries = {'hello "world"': 'hallo "welt"'}
        formatted = format_glossary_entries(entries, format_type="csv")
        assert formatted == '"hello ""world""","hallo ""welt"""'

    def test_format_glossary_entries_invalid_format(self):
        """Test that format_glossary_entries raises an error for invalid format."""
        entries = {"hello": "hallo", "world": "welt"}
        with pytest.raises(ValueError):
            format_glossary_entries(entries, format_type="invalid")

    def test_parse_glossary_entries_csv(self):
        """Test that parse_glossary_entries parses entries correctly from CSV format."""
        content = '"hello","hallo"\n"world","welt"'
        parsed = parse_glossary_entries(content, format_type="csv")
        assert parsed == {"hello": "hallo", "world": "welt"}

    def test_parse_glossary_entries_tsv(self):
        """Test that parse_glossary_entries parses entries correctly from TSV format."""
        content = "hello\thallo\nworld\twelt"
        parsed = parse_glossary_entries(content, format_type="tsv")
        assert parsed == {"hello": "hallo", "world": "welt"}

    def test_parse_glossary_entries_with_quotes_csv(self):
        """Test that parse_glossary_entries handles quotes in CSV format."""
        content = '"hello ""world""","hallo ""welt"""'
        parsed = parse_glossary_entries(content, format_type="csv")
        assert parsed == {'hello "world"': 'hallo "welt"'}

    def test_parse_glossary_entries_invalid_format(self):
        """Test that parse_glossary_entries raises an error for invalid format."""
        content = '"hello","hallo"\n"world","welt"'
        with pytest.raises(ValueError):
            parse_glossary_entries(content, format_type="invalid")

    def test_parse_glossary_entries_invalid_entry(self):
        """Test that parse_glossary_entries raises an error for invalid entry."""
        content = "hello,hallo,extra"
        with pytest.raises(ValueError):
            parse_glossary_entries(content, format_type="csv")


class TestUtilityFunctions:
    """Tests for various utility functions."""

    def test_clean_memory_resources(self):
        """Test that clean_memory_resources runs without errors."""
        with patch("gc.collect") as mock_collect:
            clean_memory_resources()
            mock_collect.assert_called_once()

    def test_sanitize_api_key_empty(self):
        """Test that sanitize_api_key handles empty keys."""
        assert sanitize_api_key("") == ""

    def test_sanitize_api_key_short(self):
        """Test that sanitize_api_key handles short keys."""
        assert sanitize_api_key("1234") == "****"

    def test_sanitize_api_key_long(self):
        """Test that sanitize_api_key sanitizes long keys."""
        assert sanitize_api_key("1234567890abcdef") == "1234****cdef"

    def test_validate_file_size_valid(self):
        """Test that validate_file_size returns True for valid file size."""
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"test")
            temp_file.flush()
            assert validate_file_size(temp_file.name, max_size_mb=1.0) is True

    def test_validate_file_size_invalid(self):
        """Test that validate_file_size returns False for invalid file size."""
        with tempfile.NamedTemporaryFile() as temp_file:
            # Write 2MB of data
            temp_file.write(b"a" * (2 * 1024 * 1024))
            temp_file.flush()
            assert validate_file_size(temp_file.name, max_size_mb=1.0) is False

    def test_validate_file_size_file_not_found(self):
        """Test that validate_file_size raises FileNotFoundError for non-existent file."""
        with pytest.raises(FileNotFoundError):
            validate_file_size("non_existent_file.txt")

    def test_get_file_mime_type(self):
        """Test that get_file_mime_type returns the correct MIME type."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            temp_file.write(b"test")
            temp_file.flush()
            assert get_file_mime_type(temp_file.name) == "text/plain"

    def test_get_file_mime_type_unknown(self):
        """Test that get_file_mime_type returns a default MIME type for unknown file types."""
        with tempfile.NamedTemporaryFile(suffix=".unknown") as temp_file:
            temp_file.write(b"test")
            temp_file.flush()
            assert get_file_mime_type(temp_file.name) == "application/octet-stream"

    def test_get_file_mime_type_file_not_found(self):
        """Test that get_file_mime_type raises FileNotFoundError for non-existent file."""
        with pytest.raises(FileNotFoundError):
            get_file_mime_type("non_existent_file.txt")
