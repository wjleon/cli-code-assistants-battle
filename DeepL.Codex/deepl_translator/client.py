"""
DeepL Translator Client
-----------------------

Provides a Python client for interacting with the DeepL API for text translation.
"""

import os
from typing import Optional
import requests

from .exceptions import DeepLException, MissingAPIKeyException

class DeepLClient:
    """
    Client for interacting with the DeepL API.

    Reads the API key from the environment variable DEEPL_API_KEY or accepts it via constructor.
    """

    DEFAULT_BASE_URL = "https://api.deepl.com/v2"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        """
        Initializes the DeepLClient.

        :param api_key: Optional DeepL API key. If not provided, reads from DEEPL_API_KEY env var.
        :param base_url: Base URL for the DeepL API. Defaults to the official DeepL endpoint.
        :raises MissingAPIKeyException: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv("DEEPL_API_KEY")
        if not self.api_key:
            raise MissingAPIKeyException(
                "DeepL API key not provided and DEEPL_API_KEY environment variable is not set."
            )
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")

    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Translates the given text into the target language.

        :param text: The input text to translate.
        :param target_language: The target language code (e.g., 'EN', 'IT', 'UK').
        :param source_language: Optional source language code.
        :param kwargs: Additional query parameters supported by DeepL API (e.g., formality).
        :return: The translated text.
        :raises DeepLException: If the API returns an error or invalid response.
        """
        url = f"{self.base_url}/translate"
        payload = {
            "auth_key": self.api_key,
            "text": text,
            "target_lang": target_language,
        }
        if source_language:
            payload["source_lang"] = source_language
        payload.update(kwargs)

        try:
            response = requests.post(url, data=payload, timeout=10)
        except requests.RequestException as e:
            raise DeepLException(f"Network error when calling DeepL API: {e}") from e

        try:
            result = response.json()
        except ValueError as e:
            raise DeepLException("Invalid JSON response from DeepL API") from e

        if response.status_code != 200:
            message = result.get("message", f"HTTP {response.status_code}")
            raise DeepLException(f"DeepL API error: {message}")

        translations = result.get("translations")
        if not translations or not isinstance(translations, list):
            raise DeepLException("Unexpected response structure: 'translations' missing or invalid")

        translated_text = translations[0].get("text")
        if translated_text is None:
            raise DeepLException("Unexpected response structure: 'text' field missing in translation")

        return translated_text.strip()