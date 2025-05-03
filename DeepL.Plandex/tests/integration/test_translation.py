"""
Integration tests for translation functionality.

These tests interact with the actual DeepL API and require a valid API key.
To run these tests, set the DEEPL_API_KEY environment variable.
"""

import os
import pytest
from typing import Dict, List, Optional

from src.client import DeepLClient
from src.models import (
    SourceLanguage,
    TargetLanguage,
    Formality,
    SplitSentences,
    PreserveFormatting,
    TextTranslationResponse,
    TranslatedText,
    SupportedLanguagesResponse,
    UsageInfo,
)
from src.exceptions import (
    DeepLError,
    AuthenticationError,
    InvalidRequestError,
)


# Skip all tests if no API key is provided
pytestmark = pytest.mark.skipif(
    "DEEPL_API_KEY" not in os.environ,
    reason="DEEPL_API_KEY environment variable not set",
)


@pytest.fixture
def client() -> DeepLClient:
    """Create a DeepL client for testing."""
    client = DeepLClient()
    yield client
    client.close()


class TestTranslation:
    """Integration tests for translation functionality."""

    def test_translate_text_string(self, client: DeepLClient) -> None:
        """Test translating a single string."""
        result = client.translate_text(
            text="Hello, world!",
            target_lang=TargetLanguage.DE,
        )

        assert isinstance(result, TextTranslationResponse)
        assert len(result.translations) == 1
        assert isinstance(result.translations[0], TranslatedText)
        assert result.translations[0].text
        assert result.translations[0].detected_source_language == SourceLanguage.EN

    def test_translate_text_list(self, client: DeepLClient) -> None:
        """Test translating a list of strings."""
        result = client.translate_text(
            text=["Hello, world!", "How are you?"],
            target_lang=TargetLanguage.DE,
        )

        assert isinstance(result, TextTranslationResponse)
        assert len(result.translations) == 2
        assert isinstance(result.translations[0], TranslatedText)
        assert result.translations[0].text
        assert result.translations[0].detected_source_language == SourceLanguage.EN
        assert isinstance(result.translations[1], TranslatedText)
        assert result.translations[1].text
        assert result.translations[1].detected_source_language == SourceLanguage.EN

    def test_translate_text_with_source_lang(self, client: DeepLClient) -> None:
        """Test translating text with a specified source language."""
        result = client.translate_text(
            text="Hello, world!",
            source_lang=SourceLanguage.EN,
            target_lang=TargetLanguage.DE,
        )

        assert isinstance(result, TextTranslationResponse)
        assert len(result.translations) == 1
        assert result.translations[0].text
        assert result.translations[0].detected_source_language == SourceLanguage.EN

    def test_translate_text_with_formality(self, client: DeepLClient) -> None:
        """Test translating text with different formality settings."""
        # Test with more formal language
        formal_result = client.translate_text(
            text="How are you?",
            target_lang=TargetLanguage.DE,
            formality=Formality.MORE,
        )

        # Test with less formal language
        informal_result = client.translate_text(
            text="How are you?",
            target_lang=TargetLanguage.DE,
            formality=Formality.LESS,
        )

        assert isinstance(formal_result, TextTranslationResponse)
        assert isinstance(informal_result, TextTranslationResponse)
        assert len(formal_result.translations) == 1
        assert len(informal_result.translations) == 1
        
        # The translations should be different due to formality
        # Note: This might not always be true for all languages and phrases,
        # but it's a reasonable expectation for German
        assert formal_result.translations[0].text != informal_result.translations[0].text

    def test_translate_text_with_split_sentences(self, client: DeepLClient) -> None:
        """Test translating text with different split_sentences settings."""
        text_with_sentences = "Hello, world! How are you today? I am fine."
        
        # Test with split sentences enabled
        split_result = client.translate_text(
            text=text_with_sentences,
            target_lang=TargetLanguage.DE,
            split_sentences=SplitSentences.ON,
        )

        # Test with split sentences disabled
        no_split_result = client.translate_text(
            text=text_with_sentences,
            target_lang=TargetLanguage.DE,
            split_sentences=SplitSentences.OFF,
        )

        assert isinstance(split_result, TextTranslationResponse)
        assert isinstance(no_split_result, TextTranslationResponse)
        assert len(split_result.translations) == 1
        assert len(no_split_result.translations) == 1
        
        # Both should return valid translations
        assert split_result.translations[0].text
        assert no_split_result.translations[0].text

    def test_translate_text_with_preserve_formatting(self, client: DeepLClient) -> None:
        """Test translating text with preserve_formatting setting."""
        text_with_formatting = "HELLO, world!"
        
        # Test with preserve formatting enabled
        preserve_result = client.translate_text(
            text=text_with_formatting,
            target_lang=TargetLanguage.DE,
            preserve_formatting=PreserveFormatting.ON,
        )

        # Test with preserve formatting disabled
        no_preserve_result = client.translate_text(
            text=text_with_formatting,
            target_lang=TargetLanguage.DE,
            preserve_formatting=PreserveFormatting.OFF,
        )

        assert isinstance(preserve_result, TextTranslationResponse)
        assert isinstance(no_preserve_result, TextTranslationResponse)
        assert len(preserve_result.translations) == 1
        assert len(no_preserve_result.translations) == 1
        
        # Both should return valid translations
        assert preserve_result.translations[0].text
        assert no_preserve_result.translations[0].text

    def test_translate_large_text(self, client: DeepLClient) -> None:
        """Test translating a large text that exceeds the chunk size."""
        # Create a text that's larger than the default chunk size (5000 characters)
        large_text = "Hello, world! " * 1000  # Approximately 14,000 characters
        
        result = client.translate_text(
            text=large_text,
            target_lang=TargetLanguage.DE,
        )

        assert isinstance(result, TextTranslationResponse)
        assert len(result.translations) == 1
        assert result.translations[0].text
        assert result.translations[0].detected_source_language == SourceLanguage.EN
        
        # The translation should be roughly proportional in length to the original
        assert len(result.translations[0].text) > 5000

    def test_translate_text_invalid_target_lang(self, client: DeepLClient) -> None:
        """Test translating text with an invalid target language."""
        with pytest.raises(InvalidRequestError):
            client.translate_text(
                text="Hello, world!",
                target_lang="INVALID",
            )

    def test_translate_text_invalid_source_lang(self, client: DeepLClient) -> None:
        """Test translating text with an invalid source language."""
        with pytest.raises(InvalidRequestError):
            client.translate_text(
                text="Hello, world!",
                source_lang="INVALID",
                target_lang=TargetLanguage.DE,
            )

    def test_translate_text_empty_text(self, client: DeepLClient) -> None:
        """Test translating empty text."""
        with pytest.raises(InvalidRequestError):
            client.translate_text(
                text="",
                target_lang=TargetLanguage.DE,
            )


class TestLanguages:
    """Integration tests for language-related functionality."""

    def test_get_source_languages(self, client: DeepLClient) -> None:
        """Test getting the list of supported source languages."""
        result = client.get_supported_languages(target=False)

        assert isinstance(result, SupportedLanguagesResponse)
        assert len(result.source_languages) > 0
        assert len(result.target_languages) == 0
        
        # Check that common languages are included
        language_codes = [lang.language for lang in result.source_languages]
        assert "EN" in language_codes
        assert "DE" in language_codes
        assert "FR" in language_codes

    def test_get_target_languages(self, client: DeepLClient) -> None:
        """Test getting the list of supported target languages."""
        result = client.get_supported_languages(target=True)

        assert isinstance(result, SupportedLanguagesResponse)
        assert len(result.target_languages) > 0
        assert len(result.source_languages) == 0
        
        # Check that common languages are included
        language_codes = [lang.language for lang in result.target_languages]
        assert "EN" in language_codes or "EN-US" in language_codes or "EN-GB" in language_codes
        assert "DE" in language_codes
        assert "FR" in language_codes
        
        # Check that at least some languages support formality
        formality_supported = any(lang.supports_formality for lang in result.target_languages)
        assert formality_supported

    def test_get_all_supported_languages(self, client: DeepLClient) -> None:
        """Test getting the list of all supported languages."""
        result = client.get_all_supported_languages()

        assert isinstance(result, SupportedLanguagesResponse)
        assert len(result.source_languages) > 0
        assert len(result.target_languages) > 0


class TestUsage:
    """Integration tests for usage-related functionality."""

    def test_get_usage(self, client: DeepLClient) -> None:
        """Test getting the usage information."""
        result = client.get_usage()

        assert isinstance(result, UsageInfo)
        assert result.character_count >= 0
        assert result.character_limit > 0
