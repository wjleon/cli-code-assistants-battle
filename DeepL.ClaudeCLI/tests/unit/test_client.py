"""
Unit tests for the DeepL API client.
"""
import os
import unittest
from unittest import mock
import json
from requests import Session, Response

from deepl.client import DeepLClient
from deepl.exceptions.api_exceptions import AuthorizationError, QuotaExceededError, ValidationError
from deepl.models.translation import TranslationResponse
from deepl.models.language import Language
from deepl.models.usage import Usage


class TestDeepLClient(unittest.TestCase):
    """Test cases for DeepLClient."""

    def setUp(self):
        """Set up test environment."""
        self.api_key = "test_api_key"
        self.client = DeepLClient(api_key=self.api_key)
        self.session_mock = mock.MagicMock(spec=Session)
        self.client.session = self.session_mock

    def create_mock_response(self, status_code=200, json_data=None, text=""):
        """Helper method to create a mock response."""
        mock_response = mock.MagicMock(spec=Response)
        mock_response.status_code = status_code
        mock_response.text = text
        
        if json_data:
            mock_response.json.return_value = json_data
            mock_response.content = json.dumps(json_data).encode()
        else:
            mock_response.json.side_effect = ValueError("No JSON content")
            mock_response.content = text.encode() if text else b""
            
        return mock_response

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = DeepLClient(api_key=self.api_key)
        self.assertEqual(client.api_key, self.api_key)
        self.assertEqual(client.base_url, client.PRO_API_URL)

    @mock.patch.dict(os.environ, {"DEEPL_API_KEY": "env_api_key"})
    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        client = DeepLClient()
        self.assertEqual(client.api_key, "env_api_key")

    def test_init_no_api_key(self):
        """Test initialization with no API key."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                DeepLClient()

    def test_free_api_detection(self):
        """Test detection of free API from API key."""
        client = DeepLClient(api_key="test_api_key:fx")
        self.assertEqual(client.base_url, client.FREE_API_URL)

    def test_translate_success(self):
        """Test successful translation."""
        # Mock response
        mock_resp = self.create_mock_response(json_data={
            "translations": [
                {
                    "detected_source_language": "ES",
                    "text": "Hello, world!"
                }
            ]
        })
        self.session_mock.request.return_value = mock_resp
        
        # Test translate method
        result = self.client.translate("Hola, mundo!", "EN")
        
        # Verify request was made correctly
        self.session_mock.request.assert_called_once()
        call_args = self.session_mock.request.call_args
        self.assertEqual(call_args[1]["method"], "POST")
        self.assertEqual(call_args[1]["url"], f"{self.client.base_url}{self.client.TRANSLATE_ENDPOINT}")
        
        # Verify request payload
        request_data = call_args[1]["json"]
        self.assertEqual(request_data["text"], "Hola, mundo!")
        self.assertEqual(request_data["target_lang"], "EN")
        
        # Verify response was parsed correctly
        self.assertIsInstance(result, TranslationResponse)
        self.assertEqual(len(result.translations), 1)
        self.assertEqual(result.translations[0].detected_source_language, "ES")
        self.assertEqual(result.translations[0].text, "Hello, world!")

    def test_translate_auth_error(self):
        """Test translation with authentication error."""
        mock_resp = self.create_mock_response(
            status_code=403, 
            json_data={"message": "Invalid API key"}
        )
        self.session_mock.request.return_value = mock_resp
        
        with self.assertRaises(AuthorizationError) as context:
            self.client.translate("Test", "EN")
            
        self.assertIn("Authentication error", str(context.exception))

    def test_translate_quota_error(self):
        """Test translation with quota exceeded error."""
        mock_resp = self.create_mock_response(
            status_code=456, 
            json_data={"message": "Quota exceeded"}
        )
        self.session_mock.request.return_value = mock_resp
        
        with self.assertRaises(QuotaExceededError) as context:
            self.client.translate("Test", "EN")
            
        self.assertIn("Quota exceeded", str(context.exception))

    def test_get_languages(self):
        """Test getting supported languages."""
        # Mock response
        mock_resp = self.create_mock_response(json_data=[
            {"language": "EN", "name": "English"},
            {"language": "DE", "name": "German", "supports_formality": True}
        ])
        self.session_mock.request.return_value = mock_resp
        
        # Test get_languages method
        result = self.client.get_languages(type="target")
        
        # Verify request was made correctly
        self.session_mock.request.assert_called_once()
        call_args = self.session_mock.request.call_args
        self.assertEqual(call_args[1]["method"], "GET")
        self.assertEqual(call_args[1]["url"], f"{self.client.base_url}{self.client.LANGUAGES_ENDPOINT}")
        self.assertEqual(call_args[1]["params"], {"type": "target"})
        
        # Verify response was parsed correctly
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Language)
        self.assertEqual(result[0].language, "EN")
        self.assertEqual(result[0].name, "English")
        self.assertEqual(result[0].supports_formality, False)
        self.assertEqual(result[1].language, "DE")
        self.assertEqual(result[1].name, "German")
        self.assertEqual(result[1].supports_formality, True)

    def test_get_usage(self):
        """Test getting usage information."""
        # Mock response
        mock_resp = self.create_mock_response(json_data={
            "character_count": 180118,
            "character_limit": 1250000
        })
        self.session_mock.request.return_value = mock_resp
        
        # Test get_usage method
        result = self.client.get_usage()
        
        # Verify request was made correctly
        self.session_mock.request.assert_called_once()
        call_args = self.session_mock.request.call_args
        self.assertEqual(call_args[1]["method"], "GET")
        self.assertEqual(call_args[1]["url"], f"{self.client.base_url}{self.client.USAGE_ENDPOINT}")
        
        # Verify response was parsed correctly
        self.assertIsInstance(result, Usage)
        self.assertEqual(result.character_count, 180118)
        self.assertEqual(result.character_limit, 1250000)
        self.assertAlmostEqual(result.character_percentage, 14.41, places=2)

    def test_context_manager(self):
        """Test client as context manager."""
        with mock.patch.object(DeepLClient, 'close') as mock_close:
            with DeepLClient(api_key=self.api_key):
                pass
            mock_close.assert_called_once()


if __name__ == "__main__":
    unittest.main()