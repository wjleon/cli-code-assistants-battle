"""
Integration tests for the DeepL API client.

This module contains tests that interact with the actual DeepL API.
These tests require a valid API key to be set in the DEEPL_API_KEY environment variable.
"""

import os
import pytest
from deepl_integration.client import DeepLClient
from deepl_integration.models import TranslationResult, Language, UsageInformation
from deepl_integration.exceptions import AuthenticationError


# Skip all tests if no API key is provided
pytestmark = pytest.mark.skipif(
    os.environ.get("DEEPL_API_KEY") is None,
    reason="DEEPL_API_KEY environment variable not set"
)


class TestDeepLClientIntegration:
    """Integration tests for the DeepLClient class."""

    @pytest.fixture
    def client(self):
        """Create a DeepLClient instance for testing."""
        return DeepLClient()

    def test_translate_single_text(self, client):
        """Test translating a single text."""
        result = client.translate("Hello world", target_lang="DE")
        
        assert isinstance(result, TranslationResult)
        assert result.text
        assert result.detected_source_language == "EN"
    
    def test_translate_multiple_texts(self, client):
        """Test translating multiple texts."""
        results = client.translate(["Hello", "World"], target_lang="DE")
        
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(result, TranslationResult) for result in results)
        assert all(result.detected_source_language == "EN" for result in results)
    
    def test_translate_with_source_lang(self, client):
        """Test translating with a specified source language."""
        result = client.translate("Hello world", target_lang="DE", source_lang="EN")
        
        assert isinstance(result, TranslationResult)
        assert result.text
        assert result.detected_source_language == "EN"
    
    def test_translate_with_formality(self, client):
        """Test translating with formality option."""
        # German supports formality
        result_formal = client.translate("Hello", target_lang="DE", formality="more")
        result_informal = client.translate("Hello", target_lang="DE", formality="less")
        
        assert isinstance(result_formal, TranslationResult)
        assert isinstance(result_informal, TranslationResult)
        # Note: The results might be the same for simple words, but the API should accept the parameter
    
    def test_get_supported_languages(self, client):
        """Test getting supported languages."""
        target_languages = client.get_supported_languages(target_type="target")
        source_languages = client.get_supported_languages(target_type="source")
        
        assert isinstance(target_languages, list)
        assert isinstance(source_languages, list)
        assert len(target_languages) > 0
        assert len(source_languages) > 0
        assert all(isinstance(lang, Language) for lang in target_languages)
        assert all(isinstance(lang, Language) for lang in source_languages)
    
    def test_get_usage_information(self, client):
        """Test getting usage information."""
        usage = client.get_usage_information()
        
        assert isinstance(usage, UsageInformation)
        assert usage.character_count >= 0
        assert usage.character_limit > 0
    
    def test_invalid_api_key(self):
        """Test using an invalid API key."""
        client = DeepLClient(api_key="invalid-api-key")
        
        with pytest.raises(AuthenticationError):
            client.translate("Hello world", target_lang="DE")
