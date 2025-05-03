"""
DeepL API client implementation.

This module provides a client for interacting with the DeepL API, following SOLID principles
and providing a clean, modular interface for translation services.
"""

import logging
import requests
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager

from .models import TranslationResult, TranslationResponse, Language, UsageInformation
from .exceptions import (
    AuthenticationError, QuotaExceededError, ValidationError,
    RateLimitError, ServerError, ConnectionError, TimeoutError, UnexpectedResponseError
)
from .utils import get_api_key, clean_text, map_error_code

# Configure logging
logger = logging.getLogger(__name__)


class DeepLClient:
    """
    Client for interacting with the DeepL API.
    
    This class follows the Single Responsibility Principle by focusing solely on
    API communication with DeepL's translation services.
    """
    
    # Base URLs for the DeepL API
    FREE_API_URL = "https://api-free.deepl.com/v2"
    PRO_API_URL = "https://api.deepl.com/v2"
    
    # API endpoints
    TRANSLATE_ENDPOINT = "/translate"
    LANGUAGES_ENDPOINT = "/languages"
    USAGE_ENDPOINT = "/usage"
    
    # Default request timeout in seconds
    DEFAULT_TIMEOUT = 10
    
    def __init__(self, api_key: Optional[str] = None, is_pro: bool = False, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the DeepL API client.
        
        Args:
            api_key: The DeepL API key. If not provided, it will be retrieved from environment variables.
            is_pro: Whether to use the Pro API URL. Defaults to False.
            timeout: Request timeout in seconds. Defaults to 10 seconds.
        """
        self.api_key = api_key or get_api_key()
        self.base_url = self.PRO_API_URL if is_pro else self.FREE_API_URL
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"DeepL-Auth-Key {self.api_key}",
            "User-Agent": "DeepLPythonClient/0.1.0",
            "Content-Type": "application/json"
        })
        logger.debug(f"Initialized DeepL client with base URL: {self.base_url}")
    
    def __del__(self):
        """
        Clean up resources when the client is garbage collected.
        
        This ensures that the session is properly closed to prevent resource leaks.
        """
        if hasattr(self, 'session'):
            self.session.close()
    
    @contextmanager
    def _handle_request_errors(self):
        """
        Context manager for handling request errors.
        
        This method provides a clean way to handle exceptions that may occur during API requests.
        """
        try:
            yield
        except requests.exceptions.Timeout:
            logger.error("Request to DeepL API timed out")
            raise TimeoutError("Request to DeepL API timed out")
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to DeepL API")
            raise ConnectionError("Failed to connect to DeepL API")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to DeepL API failed: {str(e)}")
            raise ConnectionError(f"Request to DeepL API failed: {str(e)}")
    
    def _process_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Process the API response and handle errors.
        
        Args:
            response: The response from the API.
            
        Returns:
            The JSON response data.
            
        Raises:
            Various exceptions based on the response status code.
        """
        try:
            response_json = response.json()
        except ValueError:
            logger.error("Failed to parse JSON response from DeepL API")
            raise UnexpectedResponseError("Failed to parse JSON response from DeepL API")
        
        if response.status_code != 200:
            error_message = map_error_code(response.status_code, response_json)
            logger.error(f"DeepL API error: {error_message}")
            
            if response.status_code == 401:
                raise AuthenticationError(error_message)
            elif response.status_code == 456:
                raise QuotaExceededError(error_message)
            elif response.status_code == 429:
                raise RateLimitError(error_message)
            elif response.status_code == 400:
                raise ValidationError(error_message)
            elif response.status_code >= 500:
                raise ServerError(error_message)
            else:
                raise UnexpectedResponseError(error_message)
        
        return response_json
    
    def translate(
        self,
        text: Union[str, List[str]],
        target_lang: str,
        source_lang: Optional[str] = None,
        formality: Optional[str] = None,
        split_sentences: Optional[str] = None,
        preserve_formatting: bool = False,
        tag_handling: Optional[str] = None,
        outline_detection: bool = True
    ) -> Union[TranslationResult, List[TranslationResult]]:
        """
        Translate text using the DeepL API.
        
        Args:
            text: The text to translate. Can be a single string or a list of strings.
            target_lang: The target language code (e.g., 'EN', 'DE', 'FR').
            source_lang: Optional source language code. If not provided, DeepL will auto-detect.
            formality: Optional formality level ('default', 'more', 'less').
            split_sentences: Optional sentence splitting ('0', '1', 'nonewlines').
            preserve_formatting: Whether to preserve formatting. Defaults to False.
            tag_handling: Optional tag handling ('xml', 'html').
            outline_detection: Whether to use outline detection. Defaults to True.
            
        Returns:
            If input is a single string: A TranslationResult object.
            If input is a list of strings: A list of TranslationResult objects.
            
        Raises:
            Various exceptions for API errors.
        """
        is_single_text = isinstance(text, str)
        texts = [clean_text(text)] if is_single_text else [clean_text(t) for t in text]
        
        # Prepare request parameters
        params: Dict[str, Any] = {
            "text": texts,
            "target_lang": target_lang.upper(),
        }
        
        # Add optional parameters if provided
        if source_lang:
            params["source_lang"] = source_lang.upper()
        if formality:
            params["formality"] = formality
        if split_sentences is not None:
            params["split_sentences"] = split_sentences
        if preserve_formatting:
            params["preserve_formatting"] = "1"
        if tag_handling:
            params["tag_handling"] = tag_handling
        if not outline_detection:
            params["outline_detection"] = "0"
        
        logger.debug(f"Translating text to {target_lang}")
        
        with self._handle_request_errors():
            response = self.session.post(
                f"{self.base_url}{self.TRANSLATE_ENDPOINT}",
                json=params,
                timeout=self.timeout
            )
            
            response_data = self._process_response(response)
            translation_response = TranslationResponse.from_dict(response_data)
            
            if is_single_text and translation_response.translations:
                return translation_response.translations[0]
            return translation_response.translations
    
    def get_supported_languages(self, target_type: str = "target") -> List[Language]:
        """
        Get the list of supported languages.
        
        Args:
            target_type: The type of languages to retrieve ('source' or 'target').
            
        Returns:
            A list of Language objects.
            
        Raises:
            Various exceptions for API errors.
        """
        params = {"type": target_type}
        
        logger.debug(f"Getting supported {target_type} languages")
        
        with self._handle_request_errors():
            response = self.session.get(
                f"{self.base_url}{self.LANGUAGES_ENDPOINT}",
                params=params,
                timeout=self.timeout
            )
            
            response_data = self._process_response(response)
            return [Language.from_dict(lang_data) for lang_data in response_data]
    
    def get_usage_information(self) -> UsageInformation:
        """
        Get usage information for the API key.
        
        Returns:
            A UsageInformation object.
            
        Raises:
            Various exceptions for API errors.
        """
        logger.debug("Getting usage information")
        
        with self._handle_request_errors():
            response = self.session.get(
                f"{self.base_url}{self.USAGE_ENDPOINT}",
                timeout=self.timeout
            )
            
            response_data = self._process_response(response)
            return UsageInformation.from_dict(response_data)
