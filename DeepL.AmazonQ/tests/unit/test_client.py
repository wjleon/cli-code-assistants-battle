"""
Unit tests for the client module.

This module contains tests for the DeepL API client implementation.
"""

import pytest
from unittest.mock import Mock, patch
import requests
from requests.exceptions import Timeout, ConnectionError as RequestsConnectionError

from deepl_integration.client import DeepLClient
from deepl_integration.models import TranslationResult, Language, UsageInformation
from deepl_integration.exceptions import (
    AuthenticationError, QuotaExceededError, ValidationError,
    RateLimitError, ServerError, ConnectionError, TimeoutError, UnexpectedResponseError
)


class TestDeepLClient:
    """Tests for the DeepLClient class."""

    @pytest.fixture
    def client(self):
        """Create a DeepLClient instance for testing."""
        with patch('deepl_integration.client.get_api_key', return_value='test-api-key'):
            return DeepLClient()

    def test_init(self):
        """Test initializing the client."""
        with patch('deepl_integration.client.get_api_key', return_value='test-api-key'):
            client = DeepLClient()
            
            assert client.api_key == 'test-api-key'
            assert client.base_url == DeepLClient.FREE_API_URL
            assert client.timeout == DeepLClient.DEFAULT_TIMEOUT
            assert 'Authorization' in client.session.headers
            assert client.session.headers['Authorization'] == 'DeepL-Auth-Key test-api-key'
    
    def test_init_with_custom_params(self):
        """Test initializing the client with custom parameters."""
        client = DeepLClient(api_key='custom-api-key', is_pro=True, timeout=20)
        
        assert client.api_key == 'custom-api-key'
        assert client.base_url == DeepLClient.PRO_API_URL
        assert client.timeout == 20
    
    def test_process_response_success(self, client):
        """Test processing a successful response."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        
        result = client._process_response(mock_response)
        
        assert result == {"result": "success"}
    
    def test_process_response_json_error(self, client):
        """Test processing a response with invalid JSON."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with pytest.raises(UnexpectedResponseError):
            client._process_response(mock_response)
    
    @pytest.mark.parametrize("status_code,exception_class", [
        (401, AuthenticationError),
        (456, QuotaExceededError),
        (429, RateLimitError),
        (400, ValidationError),
        (500, ServerError),
        (418, UnexpectedResponseError),  # Teapot status for testing unknown errors
    ])
    def test_process_response_error(self, client, status_code, exception_class):
        """Test processing error responses."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = status_code
        mock_response.json.return_value = {"message": "Error message"}
        
        with pytest.raises(exception_class):
            client._process_response(mock_response)
    
    def test_handle_request_errors_timeout(self, client):
        """Test handling a timeout error."""
        with pytest.raises(TimeoutError):
            with client._handle_request_errors():
                raise Timeout("Request timed out")
    
    def test_handle_request_errors_connection_error(self, client):
        """Test handling a connection error."""
        with pytest.raises(ConnectionError):
            with client._handle_request_errors():
                raise RequestsConnectionError("Connection failed")
    
    def test_translate_single_text(self, client):
        """Test translating a single text."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translations": [
                {
                    "text": "Hallo Welt",
                    "detected_source_language": "EN"
                }
            ]
        }
        
        with patch.object(client.session, 'post', return_value=mock_response):
            result = client.translate("Hello world", target_lang="DE")
            
            assert isinstance(result, TranslationResult)
            assert result.text == "Hallo Welt"
            assert result.detected_source_language == "EN"
            
            # Verify the request was made correctly
            client.session.post.assert_called_once()
            args, kwargs = client.session.post.call_args
            assert args[0] == f"{client.base_url}{client.TRANSLATE_ENDPOINT}"
            assert kwargs['json']['text'] == ["Hello world"]
            assert kwargs['json']['target_lang'] == "DE"
    
    def test_translate_multiple_texts(self, client):
        """Test translating multiple texts."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translations": [
                {
                    "text": "Hallo",
                    "detected_source_language": "EN"
                },
                {
                    "text": "Welt",
                    "detected_source_language": "EN"
                }
            ]
        }
        
        with patch.object(client.session, 'post', return_value=mock_response):
            results = client.translate(["Hello", "World"], target_lang="DE")
            
            assert isinstance(results, list)
            assert len(results) == 2
            assert results[0].text == "Hallo"
            assert results[1].text == "Welt"
    
    def test_translate_with_options(self, client):
        """Test translating with additional options."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translations": [
                {
                    "text": "Hallo Welt",
                    "detected_source_language": "EN"
                }
            ]
        }
        
        with patch.object(client.session, 'post', return_value=mock_response):
            client.translate(
                "Hello world",
                target_lang="DE",
                source_lang="EN",
                formality="more",
                split_sentences="1",
                preserve_formatting=True,
                tag_handling="xml",
                outline_detection=False
            )
            
            # Verify the request was made with all options
            args, kwargs = client.session.post.call_args
            assert kwargs['json']['source_lang'] == "EN"
            assert kwargs['json']['formality'] == "more"
            assert kwargs['json']['split_sentences'] == "1"
            assert kwargs['json']['preserve_formatting'] == "1"
            assert kwargs['json']['tag_handling'] == "xml"
            assert kwargs['json']['outline_detection'] == "0"
    
    def test_get_supported_languages(self, client):
        """Test getting supported languages."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "language": "EN",
                "name": "English",
                "supports_formality": False
            },
            {
                "language": "DE",
                "name": "German",
                "supports_formality": True
            }
        ]
        
        with patch.object(client.session, 'get', return_value=mock_response):
            languages = client.get_supported_languages()
            
            assert isinstance(languages, list)
            assert len(languages) == 2
            assert languages[0].language == "EN"
            assert languages[0].name == "English"
            assert languages[0].supports_formality is False
            assert languages[1].language == "DE"
            assert languages[1].name == "German"
            assert languages[1].supports_formality is True
            
            # Verify the request was made correctly
            client.session.get.assert_called_once()
            args, kwargs = client.session.get.call_args
            assert args[0] == f"{client.base_url}{client.LANGUAGES_ENDPOINT}"
            assert kwargs['params']['type'] == "target"
    
    def test_get_usage_information(self, client):
        """Test getting usage information."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "character_count": 1000,
            "character_limit": 5000
        }
        
        with patch.object(client.session, 'get', return_value=mock_response):
            usage = client.get_usage_information()
            
            assert isinstance(usage, UsageInformation)
            assert usage.character_count == 1000
            assert usage.character_limit == 5000
            
            # Verify the request was made correctly
            client.session.get.assert_called_once()
            args, kwargs = client.session.get.call_args
            assert args[0] == f"{client.base_url}{client.USAGE_ENDPOINT}"
