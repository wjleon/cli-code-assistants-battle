"""
Unit tests for the config module.
"""

import os
import pytest
from unittest.mock import patch

from src.config import (
    get_api_key,
    get_api_url,
    get_config,
    APIKeyNotFoundError,
    InvalidAPIKeyError,
    _is_valid_api_key,
)


class TestConfig:
    """Tests for the config module."""

    def test_is_valid_api_key_with_valid_free_key(self):
        """Test that a valid free API key is recognized."""
        # Free API key (starts with 'f' followed by 31 alphanumeric characters)
        api_key = "f" + "a" * 31
        assert _is_valid_api_key(api_key) is True

    def test_is_valid_api_key_with_valid_pro_key(self):
        """Test that a valid pro API key is recognized."""
        # Pro API key (32 alphanumeric characters)
        api_key = "a" * 32
        assert _is_valid_api_key(api_key) is True

    def test_is_valid_api_key_with_invalid_key_too_short(self):
        """Test that an API key that is too short is rejected."""
        api_key = "a" * 31
        assert _is_valid_api_key(api_key) is False

    def test_is_valid_api_key_with_invalid_key_empty(self):
        """Test that an empty API key is rejected."""
        api_key = ""
        assert _is_valid_api_key(api_key) is False

    def test_is_valid_api_key_with_invalid_key_none(self):
        """Test that a None API key is rejected."""
        api_key = None
        assert _is_valid_api_key(api_key) is False

    def test_is_valid_api_key_with_invalid_key_special_chars(self):
        """Test that an API key with special characters is rejected."""
        api_key = "f" + "a" * 30 + "!"
        assert _is_valid_api_key(api_key) is False

    @patch.dict(os.environ, {"DEEPL_API_KEY": "f" + "a" * 31})
    def test_get_api_key_with_valid_key(self):
        """Test that get_api_key returns the API key when it's valid."""
        api_key = get_api_key()
        assert api_key == "f" + "a" * 31

    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_with_missing_key(self):
        """Test that get_api_key raises an exception when the API key is missing."""
        with pytest.raises(APIKeyNotFoundError):
            get_api_key()

    @patch.dict(os.environ, {"DEEPL_API_KEY": "invalid"})
    def test_get_api_key_with_invalid_key(self):
        """Test that get_api_key raises an exception when the API key is invalid."""
        with pytest.raises(InvalidAPIKeyError):
            get_api_key()

    @patch.dict(os.environ, {"DEEPL_API_KEY": "f" + "a" * 31})
    def test_get_api_url_with_free_key(self):
        """Test that get_api_url returns the free API URL when using a free API key."""
        api_url = get_api_url()
        assert api_url == "https://api-free.deepl.com/v2"

    @patch.dict(os.environ, {"DEEPL_API_KEY": "a" * 32})
    def test_get_api_url_with_pro_key(self):
        """Test that get_api_url returns the pro API URL when using a pro API key."""
        api_url = get_api_url()
        assert api_url == "https://api.deepl.com/v2"

    @patch.dict(os.environ, {"DEEPL_API_KEY": "f" + "a" * 31})
    def test_get_api_url_with_explicit_free(self):
        """Test that get_api_url returns the free API URL when explicitly specified."""
        api_url = get_api_url(is_free_api=True)
        assert api_url == "https://api-free.deepl.com/v2"

    @patch.dict(os.environ, {"DEEPL_API_KEY": "f" + "a" * 31})
    def test_get_api_url_with_explicit_pro(self):
        """Test that get_api_url returns the pro API URL when explicitly specified."""
        api_url = get_api_url(is_free_api=False)
        assert api_url == "https://api.deepl.com/v2"

    @patch.dict(os.environ, {"DEEPL_API_KEY": "f" + "a" * 31, "DEEPL_TIMEOUT": "20", "DEEPL_MAX_RETRIES": "5"})
    def test_get_config_with_custom_env_vars(self):
        """Test that get_config returns the correct configuration with custom environment variables."""
        config = get_config()
        assert config["api_key"] == "f" + "a" * 31
        assert config["api_url"] == "https://api-free.deepl.com/v2"
        assert config["is_free_api"] is True
        assert config["timeout"] == 20
        assert config["max_retries"] == 5

    @patch.dict(os.environ, {"DEEPL_API_KEY": "f" + "a" * 31})
    def test_get_config_with_default_values(self):
        """Test that get_config returns the correct configuration with default values."""
        config = get_config()
        assert config["api_key"] == "f" + "a" * 31
        assert config["api_url"] == "https://api-free.deepl.com/v2"
        assert config["is_free_api"] is True
        assert config["timeout"] == 10
        assert config["max_retries"] == 3
