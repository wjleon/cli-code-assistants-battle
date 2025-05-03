"""
Unit tests for the utils module.

This module contains tests for the utility functions used in the DeepL API integration.
"""

import os
import pytest
from deepl_integration.utils import get_api_key, clean_text, map_error_code
from deepl_integration.exceptions import AuthenticationError


class TestGetApiKey:
    """Tests for the get_api_key function."""

    def test_get_api_key_success(self, monkeypatch):
        """Test getting the API key when it is set."""
        monkeypatch.setenv("DEEPL_API_KEY", "test-api-key")
        
        api_key = get_api_key()
        
        assert api_key == "test-api-key"
    
    def test_get_api_key_not_set(self, monkeypatch):
        """Test getting the API key when it is not set."""
        monkeypatch.delenv("DEEPL_API_KEY", raising=False)
        
        with pytest.raises(AuthenticationError) as excinfo:
            get_api_key()
        
        assert "DEEPL_API_KEY environment variable not set" in str(excinfo.value)


class TestCleanText:
    """Tests for the clean_text function."""

    def test_clean_text_with_whitespace(self):
        """Test cleaning text with excessive whitespace."""
        text = "  Hello   world  "
        cleaned = clean_text(text)
        
        assert cleaned == "Hello world"
    
    def test_clean_text_with_newlines(self):
        """Test cleaning text with newlines."""
        text = "Hello\nworld"
        cleaned = clean_text(text)
        
        assert cleaned == "Hello world"
    
    def test_clean_text_with_tabs(self):
        """Test cleaning text with tabs."""
        text = "Hello\tworld"
        cleaned = clean_text(text)
        
        assert cleaned == "Hello world"
    
    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        text = ""
        cleaned = clean_text(text)
        
        assert cleaned == ""
    
    def test_clean_text_none(self):
        """Test cleaning None."""
        cleaned = clean_text(None)
        
        assert cleaned == ""


class TestMapErrorCode:
    """Tests for the map_error_code function."""

    def test_map_error_code_known(self):
        """Test mapping a known error code."""
        error_message = map_error_code(401)
        
        assert "Authentication failed" in error_message
    
    def test_map_error_code_unknown(self):
        """Test mapping an unknown error code."""
        error_message = map_error_code(499)
        
        assert "Unknown error: HTTP 499" in error_message
    
    def test_map_error_code_with_response_message(self):
        """Test mapping an error code with a response message."""
        response_json = {"message": "Custom error message"}
        error_message = map_error_code(400, response_json)
        
        assert error_message == "Custom error message"
