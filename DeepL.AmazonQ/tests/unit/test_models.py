"""
Unit tests for the models module.

This module contains tests for the data models used in the DeepL API integration.
"""

import pytest
from deepl_integration.models import (
    TranslationResult, TranslationResponse, Language, UsageInformation
)


class TestTranslationResult:
    """Tests for the TranslationResult class."""

    def test_from_dict(self):
        """Test creating a TranslationResult from a dictionary."""
        data = {
            "text": "Hello world",
            "detected_source_language": "EN"
        }
        result = TranslationResult.from_dict(data)
        
        assert result.text == "Hello world"
        assert result.detected_source_language == "EN"
    
    def test_from_dict_with_missing_fields(self):
        """Test creating a TranslationResult with missing fields."""
        data = {}
        result = TranslationResult.from_dict(data)
        
        assert result.text == ""
        assert result.detected_source_language == ""


class TestTranslationResponse:
    """Tests for the TranslationResponse class."""

    def test_from_dict(self):
        """Test creating a TranslationResponse from a dictionary."""
        data = {
            "translations": [
                {
                    "text": "Hello world",
                    "detected_source_language": "EN"
                },
                {
                    "text": "Goodbye world",
                    "detected_source_language": "EN"
                }
            ]
        }
        response = TranslationResponse.from_dict(data)
        
        assert len(response.translations) == 2
        assert response.translations[0].text == "Hello world"
        assert response.translations[0].detected_source_language == "EN"
        assert response.translations[1].text == "Goodbye world"
        assert response.translations[1].detected_source_language == "EN"
    
    def test_from_dict_with_empty_translations(self):
        """Test creating a TranslationResponse with empty translations."""
        data = {"translations": []}
        response = TranslationResponse.from_dict(data)
        
        assert len(response.translations) == 0
    
    def test_from_dict_with_missing_translations(self):
        """Test creating a TranslationResponse with missing translations."""
        data = {}
        response = TranslationResponse.from_dict(data)
        
        assert len(response.translations) == 0


class TestLanguage:
    """Tests for the Language class."""

    def test_from_dict(self):
        """Test creating a Language from a dictionary."""
        data = {
            "language": "EN",
            "name": "English",
            "supports_formality": True
        }
        language = Language.from_dict(data)
        
        assert language.language == "EN"
        assert language.name == "English"
        assert language.supports_formality is True
    
    def test_from_dict_with_missing_fields(self):
        """Test creating a Language with missing fields."""
        data = {}
        language = Language.from_dict(data)
        
        assert language.language == ""
        assert language.name == ""
        assert language.supports_formality is False


class TestUsageInformation:
    """Tests for the UsageInformation class."""

    def test_from_dict(self):
        """Test creating a UsageInformation from a dictionary."""
        data = {
            "character_count": 1000,
            "character_limit": 5000
        }
        usage = UsageInformation.from_dict(data)
        
        assert usage.character_count == 1000
        assert usage.character_limit == 5000
    
    def test_from_dict_with_missing_fields(self):
        """Test creating a UsageInformation with missing fields."""
        data = {}
        usage = UsageInformation.from_dict(data)
        
        assert usage.character_count == 0
        assert usage.character_limit == 0
    
    def test_character_percentage(self):
        """Test calculating the character percentage."""
        usage = UsageInformation(character_count=1000, character_limit=5000)
        
        assert usage.character_percentage == 20.0
    
    def test_character_percentage_with_zero_limit(self):
        """Test calculating the character percentage with a zero limit."""
        usage = UsageInformation(character_count=1000, character_limit=0)
        
        assert usage.character_percentage == 0.0
