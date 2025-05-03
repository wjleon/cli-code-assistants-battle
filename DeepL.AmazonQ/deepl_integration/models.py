"""
Data models for the DeepL API integration.

This module defines the data models used to represent the request and response objects
when interacting with the DeepL API. These models provide type safety and validation.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class TranslationResult:
    """Represents a translation result from the DeepL API."""
    text: str
    detected_source_language: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationResult':
        """
        Create a TranslationResult instance from a dictionary.

        Args:
            data: Dictionary containing translation result data.

        Returns:
            A TranslationResult instance.
        """
        return cls(
            text=data.get('text', ''),
            detected_source_language=data.get('detected_source_language', '')
        )


@dataclass
class TranslationResponse:
    """Represents the response from a translation request to the DeepL API."""
    translations: List[TranslationResult]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationResponse':
        """
        Create a TranslationResponse instance from a dictionary.

        Args:
            data: Dictionary containing translation response data.

        Returns:
            A TranslationResponse instance.
        """
        translations = [
            TranslationResult.from_dict(translation)
            for translation in data.get('translations', [])
        ]
        return cls(translations=translations)


@dataclass
class Language:
    """Represents a language supported by the DeepL API."""
    language: str
    name: str
    supports_formality: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Language':
        """
        Create a Language instance from a dictionary.

        Args:
            data: Dictionary containing language data.

        Returns:
            A Language instance.
        """
        return cls(
            language=data.get('language', ''),
            name=data.get('name', ''),
            supports_formality=data.get('supports_formality', False)
        )


@dataclass
class UsageInformation:
    """Represents usage information from the DeepL API."""
    character_count: int
    character_limit: int

    @property
    def character_percentage(self) -> float:
        """
        Calculate the percentage of the character limit used.

        Returns:
            The percentage of the character limit used.
        """
        if self.character_limit == 0:
            return 0.0
        return (self.character_count / self.character_limit) * 100

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageInformation':
        """
        Create a UsageInformation instance from a dictionary.

        Args:
            data: Dictionary containing usage information data.

        Returns:
            A UsageInformation instance.
        """
        return cls(
            character_count=data.get('character_count', 0),
            character_limit=data.get('character_limit', 0)
        )
