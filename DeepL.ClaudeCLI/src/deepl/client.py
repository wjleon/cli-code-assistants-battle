"""
Core client for the DeepL API.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from deepl.exceptions.api_exceptions import DeepLAPIError, handle_api_error, ConnectionError, ValidationError
from deepl.models.translation import TranslationRequest, TranslationResponse
from deepl.models.language import Language, SupportedLanguages
from deepl.models.usage import Usage


# Configure logging
logger = logging.getLogger(__name__)


class DeepLClient:
    """
    Client for the DeepL API.
    
    This class provides methods to interact with the DeepL API for translation services.
    """
    
    # Base URLs for the API
    FREE_API_URL = "https://api-free.deepl.com/v2"
    PRO_API_URL = "https://api.deepl.com/v2"
    
    # Endpoints
    TRANSLATE_ENDPOINT = "/translate"
    LANGUAGES_ENDPOINT = "/languages"
    USAGE_ENDPOINT = "/usage"
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5
    ):
        """
        Initialize the DeepL API client.
        
        Args:
            api_key: DeepL API key. If not provided, it will try to read from the DEEPL_API_KEY environment variable.
            base_url: Base URL for the API. If not provided, it will be determined from the API key.
            timeout: Timeout for API requests in seconds.
            max_retries: Maximum number of retries for failed requests.
            backoff_factor: Backoff factor for retries.
        
        Raises:
            ValueError: If api_key is not provided and not available in the environment.
        """
        # Get API key from environment if not provided
        self.api_key = api_key or os.environ.get("DEEPL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not provided. Please provide an API key or set the DEEPL_API_KEY environment variable."
            )
        
        # Determine base URL from API key if not provided
        self.base_url = base_url
        if not self.base_url:
            self.base_url = self.FREE_API_URL if self.api_key.endswith(":fx") else self.PRO_API_URL
            
        # Request settings
        self.timeout = timeout
        
        # Create a session with retry capabilities
        self.session = self._create_session(max_retries, backoff_factor)
        
        # Common headers
        self.headers = {
            "Authorization": f"DeepL-Auth-Key {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "deepl-python/0.1.0",
        }
        
        logger.debug(f"DeepL client initialized with base URL: {self.base_url}")
    
    def _create_session(self, max_retries: int, backoff_factor: float) -> requests.Session:
        """
        Create a requests session with retry capabilities.
        
        Args:
            max_retries: Maximum number of retries for failed requests.
            backoff_factor: Backoff factor for retries.
            
        Returns:
            A configured requests session.
        """
        session = requests.Session()
        
        # Define retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        
        # Apply retry strategy to session
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None, 
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the DeepL API.
        
        Args:
            method: HTTP method to use (GET, POST, etc.)
            endpoint: API endpoint to call
            params: URL parameters to include
            data: JSON data to send in the request body
            headers: Additional headers to include
            files: Files to upload
            
        Returns:
            The API response as a dictionary
            
        Raises:
            ConnectionError: If there's a network error
            DeepLAPIError: If the API returns an error
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)
            
        # For multipart requests, don't set Content-Type as requests will set it automatically
        if files:
            request_headers.pop("Content-Type", None)
        
        try:
            logger.debug(f"Making {method} request to {url}")
            if data:
                logger.debug(f"Request data: {json.dumps(data)}")
                
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                files=files,
                timeout=self.timeout,
            )
            
            # Check for HTTP errors
            if response.status_code >= 400:
                try:
                    error_body = response.json()
                except json.JSONDecodeError:
                    error_body = {"message": response.text}
                    
                logger.error(f"API error: {response.status_code} - {error_body}")
                raise handle_api_error(response.status_code, error_body)
            
            # Return JSON response
            if response.content:
                return response.json()
            else:
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error: {str(e)}")
            raise ConnectionError(f"Connection to DeepL API failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in response: {str(e)}")
            raise DeepLAPIError(f"Invalid JSON in response: {str(e)}")
    
    def translate(
        self, 
        text: Union[str, List[str]], 
        target_lang: str, 
        source_lang: Optional[str] = None,
        formality: Optional[str] = None,
        preserve_formatting: Optional[bool] = None,
        tag_handling: Optional[str] = None,
        split_sentences: Optional[Union[str, bool]] = None
    ) -> TranslationResponse:
        """
        Translate text using the DeepL API.
        
        Args:
            text: Text to translate. Can be a single string or a list of strings.
            target_lang: Target language code (e.g., "EN", "DE").
            source_lang: Source language code. If not provided, DeepL will auto-detect.
            formality: Desired formality level ("default", "more", "less", "prefer_more", "prefer_less").
            preserve_formatting: Whether to preserve formatting.
            tag_handling: Type of tags to handle ("xml", "html").
            split_sentences: How to split sentences ("none", "0", "1", "nonewlines", all).
            
        Returns:
            TranslationResponse object containing the translations.
            
        Raises:
            ValidationError: If the request parameters are invalid.
            DeepLAPIError: For other API errors.
        """
        # Create and validate request
        try:
            request = TranslationRequest(
                text=text,
                target_lang=target_lang,
                source_lang=source_lang,
                formality=formality,
                preserve_formatting=preserve_formatting,
                tag_handling=tag_handling,
                split_sentences=split_sentences
            )
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValidationError(f"Invalid translation request: {str(e)}")
        
        # Make API request
        data = request.to_api_request()
        response_data = self._make_request("POST", self.TRANSLATE_ENDPOINT, data=data)
        
        # Convert response to model
        try:
            return TranslationResponse(**response_data)
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            raise DeepLAPIError(f"Error parsing translation response: {str(e)}")
    
    def get_languages(self, type: str = "source") -> List[Language]:
        """
        Get supported languages from the DeepL API.
        
        Args:
            type: Type of languages to retrieve ("source" or "target").
            
        Returns:
            List of Language objects.
            
        Raises:
            ValidationError: If the type parameter is invalid.
            DeepLAPIError: For other API errors.
        """
        if type not in ["source", "target"]:
            raise ValidationError(f"Invalid language type: {type}. Must be 'source' or 'target'.")
        
        params = {"type": type}
        response_data = self._make_request("GET", self.LANGUAGES_ENDPOINT, params=params)
        
        try:
            return [Language(**lang) for lang in response_data]
        except Exception as e:
            logger.error(f"Error parsing languages response: {str(e)}")
            raise DeepLAPIError(f"Error parsing languages response: {str(e)}")
    
    def get_supported_languages(self) -> SupportedLanguages:
        """
        Get all supported languages from the DeepL API.
        
        Returns:
            SupportedLanguages object containing lists of source and target languages.
            
        Raises:
            DeepLAPIError: For API errors.
        """
        # Get source languages
        source_languages = self.get_languages(type="source")
        
        # Get target languages
        target_languages = self.get_languages(type="target")
        
        return SupportedLanguages(source=source_languages, target=target_languages)
    
    def get_usage(self) -> Usage:
        """
        Get usage information from the DeepL API.
        
        Returns:
            Usage object containing usage information.
            
        Raises:
            DeepLAPIError: For API errors.
        """
        response_data = self._make_request("GET", self.USAGE_ENDPOINT)
        
        try:
            return Usage(**response_data)
        except Exception as e:
            logger.error(f"Error parsing usage response: {str(e)}")
            raise DeepLAPIError(f"Error parsing usage response: {str(e)}")
    
    def close(self) -> None:
        """Close the client session."""
        self.session.close()
        
    def __enter__(self):
        """Support for context manager protocol."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager protocol."""
        self.close()