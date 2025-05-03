"""
Unit tests for the client module.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock, call, mock_open

import requests

from src.client import DeepLClient
from src.models import (
    SourceLanguage,
    TargetLanguage,
    Formality,
    SplitSentences,
    PreserveFormatting,
    TagHandling,
    OutlineDetection,
    GlossaryFormat,
    TextTranslationRequest,
    TextTranslationResponse,
    TranslatedText,
    LanguageInfo,
    SupportedLanguagesResponse,
    UsageInfo,
    GlossaryInfo,
    GlossaryListResponse,
    GlossaryCreateRequest,
    DocumentTranslationRequest,
    DocumentTranslationResponse,
    DocumentTranslationStatusResponse,
    DocumentTranslationResult,
)
from src.exceptions import (
    DeepLError,
    AuthenticationError,
    InvalidRequestError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    TooManyRequestsError,
    UnsupportedLanguageError,
    TextTooLargeError,
    DocumentTooLargeError,
    ResourceNotFoundError,
    GlossaryNotFoundError,
    GlossaryLimitExceededError,
    DocumentTranslationError,
    DocumentUploadError,
    DocumentDownloadError,
    DocumentTranslationTimeoutError,
)


class MockResponse:
    """Mock response for requests."""
    
    def __init__(self, status_code=200, json_data=None, content=None, ok=True):
        self.status_code = status_code
        self.json_data = json_data or {}
        self.content = content or b""
        self.ok = ok
    
    def json(self):
        return self.json_data
    
    def iter_content(self, chunk_size=8192):
        yield self.content


class TestDeepLClient:
    """Tests for the DeepLClient class."""
    
    @patch("src.client.get_config")
    def test_init_with_defaults(self, mock_get_config):
        """Test that DeepLClient initializes with default values."""
        mock_get_config.return_value = {
            "api_key": "test_api_key",
            "api_url": "https://api.deepl.com/v2",
            "is_free_api": False,
            "timeout": 10,
            "max_retries": 3,
        }
        
        client = DeepLClient()
        
        assert client.api_key == "test_api_key"
        assert client.api_url == "https://api.deepl.com/v2"
        assert client.timeout == 10
        assert client.max_retries == 3
    
    @patch("src.client.get_config")
    def test_init_with_custom_values(self, mock_get_config):
        """Test that DeepLClient initializes with custom values."""
        mock_get_config.return_value = {
            "api_key": "default_api_key",
            "api_url": "https://api.deepl.com/v2",
            "is_free_api": False,
            "timeout": 10,
            "max_retries": 3,
        }
        
        client = DeepLClient(
            api_key="custom_api_key",
            api_url="https://custom-api.deepl.com/v2",
            timeout=20,
            max_retries=5,
        )
        
        assert client.api_key == "custom_api_key"
        assert client.api_url == "https://custom-api.deepl.com/v2"
        assert client.timeout == 20
        assert client.max_retries == 5
    
    def test_handle_response_success(self):
        """Test that _handle_response returns the response data when the response is successful."""
        client = DeepLClient(api_key="test_api_key")
        response = MockResponse(
            status_code=200,
            json_data={"key": "value"},
            ok=True,
        )
        
        result = client._handle_response(response)
        
        assert result == {"key": "value"}
    
    def test_handle_response_error(self):
        """Test that _handle_response raises an exception when the response is an error."""
        client = DeepLClient(api_key="test_api_key")
        response = MockResponse(
            status_code=401,
            json_data={"message": "Authentication failed"},
            ok=False,
        )
        
        with pytest.raises(AuthenticationError):
            client._handle_response(response)
    
    def test_handle_response_json_decode_error(self):
        """Test that _handle_response handles JSON decode errors."""
        client = DeepLClient(api_key="test_api_key")
        response = MagicMock()
        response.ok = True
        response.content = b"invalid json"
        response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        
        result = client._handle_response(response)
        
        assert result == {}
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_translate_text_with_string(self, mock_safe_request, mock_managed_session):
        """Test that translate_text works with a string."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            json_data={
                "translations": [
                    {
                        "text": "Hallo, Welt!",
                        "detected_source_language": "EN",
                    }
                ]
            }
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.translate_text(
            text="Hello, world!",
            target_lang=TargetLanguage.DE,
        )
        
        assert isinstance(result, TextTranslationResponse)
        assert len(result.translations) == 1
        assert result.translations[0].text == "Hallo, Welt!"
        assert result.translations[0].detected_source_language == SourceLanguage.EN
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="POST",
            url="https://api.deepl.com/v2/translate",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            json={"text": ["Hello, world!"], "target_lang": "DE"},
            timeout=10,
        )
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_translate_text_with_list(self, mock_safe_request, mock_managed_session):
        """Test that translate_text works with a list of strings."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            json_data={
                "translations": [
                    {
                        "text": "Hallo, Welt!",
                        "detected_source_language": "EN",
                    },
                    {
                        "text": "Wie geht es dir?",
                        "detected_source_language": "EN",
                    },
                ]
            }
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.translate_text(
            text=["Hello, world!", "How are you?"],
            target_lang=TargetLanguage.DE,
        )
        
        assert isinstance(result, TextTranslationResponse)
        assert len(result.translations) == 2
        assert result.translations[0].text == "Hallo, Welt!"
        assert result.translations[0].detected_source_language == SourceLanguage.EN
        assert result.translations[1].text == "Wie geht es dir?"
        assert result.translations[1].detected_source_language == SourceLanguage.EN
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="POST",
            url="https://api.deepl.com/v2/translate",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            json={"text": ["Hello, world!", "How are you?"], "target_lang": "DE"},
            timeout=10,
        )
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_translate_text_with_all_parameters(self, mock_safe_request, mock_managed_session):
        """Test that translate_text works with all parameters."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            json_data={
                "translations": [
                    {
                        "text": "Hallo, Welt!",
                        "detected_source_language": "EN",
                    }
                ]
            }
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.translate_text(
            text="Hello, world!",
            target_lang=TargetLanguage.DE,
            source_lang=SourceLanguage.EN,
            split_sentences=SplitSentences.OFF,
            preserve_formatting=PreserveFormatting.ON,
            formality=Formality.MORE,
            glossary_id="123",
            tag_handling=TagHandling.XML,
            outline_detection=OutlineDetection.OFF,
            non_splitting_tags=["p", "div"],
            splitting_tags=["br"],
            ignore_tags=["span"],
        )
        
        assert isinstance(result, TextTranslationResponse)
        assert len(result.translations) == 1
        assert result.translations[0].text == "Hallo, Welt!"
        assert result.translations[0].detected_source_language == SourceLanguage.EN
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="POST",
            url="https://api.deepl.com/v2/translate",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            json={
                "text": ["Hello, world!"],
                "target_lang": "DE",
                "source_lang": "EN",
                "split_sentences": "0",
                "preserve_formatting": "1",
                "formality": "more",
                "glossary_id": "123",
                "tag_handling": "xml",
                "outline_detection": "0",
                "non_splitting_tags": "p,div",
                "splitting_tags": "br",
                "ignore_tags": "span",
            },
            timeout=10,
        )
    
    @patch("src.client.chunk_text")
    @patch("src.client.DeepLClient.translate_text")
    def test_translate_large_text(self, mock_translate_text, mock_chunk_text):
        """Test that _translate_large_text splits large text into chunks."""
        mock_chunk_text.return_value = ["Chunk 1", "Chunk 2"]
        
        mock_translate_text.side_effect = [
            TextTranslationResponse(
                translations=[
                    TranslatedText(
                        text="Translated Chunk 1",
                        detected_source_language=SourceLanguage.EN,
                    )
                ]
            ),
            TextTranslationResponse(
                translations=[
                    TranslatedText(
                        text="Translated Chunk 2",
                        detected_source_language=SourceLanguage.EN,
                    )
                ]
            ),
        ]
        
        client = DeepLClient(api_key="test_api_key")
        request = TextTranslationRequest(
            text="Large text" * 1000,
            target_lang=TargetLanguage.DE,
        )
        
        result = client._translate_large_text(request)
        
        assert isinstance(result, TextTranslationResponse)
        assert len(result.translations) == 1
        assert result.translations[0].text == "Translated Chunk 1Translated Chunk 2"
        assert result.translations[0].detected_source_language == SourceLanguage.EN
        
        mock_chunk_text.assert_called_once_with("Large text" * 1000, max_chunk_size=5000)
        assert mock_translate_text.call_count == 2
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_get_usage(self, mock_safe_request, mock_managed_session):
        """Test that get_usage returns the usage information."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            json_data={
                "character_count": 1234,
                "character_limit": 5678,
            }
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.get_usage()
        
        assert isinstance(result, UsageInfo)
        assert result.character_count == 1234
        assert result.character_limit == 5678
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="GET",
            url="https://api.deepl.com/v2/usage",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            timeout=10,
        )
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_get_supported_languages_source(self, mock_safe_request, mock_managed_session):
        """Test that get_supported_languages returns the supported source languages."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            json_data=[
                {
                    "language": "EN",
                    "name": "English",
                },
                {
                    "language": "DE",
                    "name": "German",
                },
            ]
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.get_supported_languages(target=False)
        
        assert isinstance(result, SupportedLanguagesResponse)
        assert len(result.source_languages) == 2
        assert result.source_languages[0].language == "EN"
        assert result.source_languages[0].name == "English"
        assert result.source_languages[1].language == "DE"
        assert result.source_languages[1].name == "German"
        assert len(result.target_languages) == 0
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="GET",
            url="https://api.deepl.com/v2/languages",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            params={"type": "source"},
            timeout=10,
        )
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_get_supported_languages_target(self, mock_safe_request, mock_managed_session):
        """Test that get_supported_languages returns the supported target languages."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            json_data=[
                {
                    "language": "EN",
                    "name": "English",
                    "supports_formality": True,
                },
                {
                    "language": "DE",
                    "name": "German",
                    "supports_formality": True,
                },
            ]
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.get_supported_languages(target=True)
        
        assert isinstance(result, SupportedLanguagesResponse)
        assert len(result.target_languages) == 2
        assert result.target_languages[0].language == "EN"
        assert result.target_languages[0].name == "English"
        assert result.target_languages[0].supports_formality is True
        assert result.target_languages[1].language == "DE"
        assert result.target_languages[1].name == "German"
        assert result.target_languages[1].supports_formality is True
        assert len(result.source_languages) == 0
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="GET",
            url="https://api.deepl.com/v2/languages",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            params={"type": "target"},
            timeout=10,
        )
    
    @patch("src.client.DeepLClient.get_supported_languages")
    def test_get_all_supported_languages(self, mock_get_supported_languages):
        """Test that get_all_supported_languages returns all supported languages."""
        mock_get_supported_languages.side_effect = [
            SupportedLanguagesResponse(
                source_languages=[
                    LanguageInfo(language="EN", name="English"),
                    LanguageInfo(language="DE", name="German"),
                ],
                target_languages=[],
            ),
            SupportedLanguagesResponse(
                source_languages=[],
                target_languages=[
                    LanguageInfo(language="EN", name="English", supports_formality=True),
                    LanguageInfo(language="DE", name="German", supports_formality=True),
                ],
            ),
        ]
        
        client = DeepLClient(api_key="test_api_key")
        result = client.get_all_supported_languages()
        
        assert isinstance(result, SupportedLanguagesResponse)
        assert len(result.source_languages) == 2
        assert result.source_languages[0].language == "EN"
        assert result.source_languages[0].name == "English"
        assert result.source_languages[1].language == "DE"
        assert result.source_languages[1].name == "German"
        assert len(result.target_languages) == 2
        assert result.target_languages[0].language == "EN"
        assert result.target_languages[0].name == "English"
        assert result.target_languages[0].supports_formality is True
        assert result.target_languages[1].language == "DE"
        assert result.target_languages[1].name == "German"
        assert result.target_languages[1].supports_formality is True
        
        mock_get_supported_languages.assert_has_calls([
            call(target=False),
            call(target=True),
        ])
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_create_glossary(self, mock_safe_request, mock_managed_session):
        """Test that create_glossary creates a glossary."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            json_data={
                "glossary_id": "123",
                "name": "My Glossary",
                "source_lang": "EN",
                "target_lang": "DE",
                "creation_time": "2021-01-01T00:00:00Z",
                "entry_count": 2,
            }
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.create_glossary(
            name="My Glossary",
            source_lang=SourceLanguage.EN,
            target_lang=TargetLanguage.DE,
            entries={"hello": "hallo", "world": "welt"},
        )
        
        assert isinstance(result, GlossaryInfo)
        assert result.glossary_id == "123"
        assert result.name == "My Glossary"
        assert result.source_lang == SourceLanguage.EN
        assert result.target_lang == TargetLanguage.DE
        assert result.creation_time == "2021-01-01T00:00:00Z"
        assert result.entry_count == 2
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="POST",
            url="https://api.deepl.com/v2/glossaries",
            headers={
                "Authorization": "DeepL-Auth-Key test_api_key",
                "Content-Type": "application/json",
            },
            json={
                "name": "My Glossary",
                "source_lang": "EN",
                "target_lang": "DE",
                "entries": '"hello","hallo"\n"world","welt"',
                "entries_format": "csv",
            },
            timeout=10,
        )
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_get_glossary(self, mock_safe_request, mock_managed_session):
        """Test that get_glossary returns a glossary."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            json_data={
                "glossary_id": "123",
                "name": "My Glossary",
                "source_lang": "EN",
                "target_lang": "DE",
                "creation_time": "2021-01-01T00:00:00Z",
                "entry_count": 2,
            }
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.get_glossary(glossary_id="123")
        
        assert isinstance(result, GlossaryInfo)
        assert result.glossary_id == "123"
        assert result.name == "My Glossary"
        assert result.source_lang == SourceLanguage.EN
        assert result.target_lang == TargetLanguage.DE
        assert result.creation_time == "2021-01-01T00:00:00Z"
        assert result.entry_count == 2
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="GET",
            url="https://api.deepl.com/v2/glossaries/123",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            timeout=10,
        )
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    @patch("src.client.parse_glossary_entries")
    def test_get_glossary_entries(self, mock_parse_glossary_entries, mock_safe_request, mock_managed_session):
        """Test that get_glossary_entries returns glossary entries."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            content=b'"hello","hallo"\n"world","welt"',
            ok=True,
        )
        mock_safe_request.return_value = mock_response
        
        mock_parse_glossary_entries.return_value = {"hello": "hallo", "world": "welt"}
        
        client = DeepLClient(api_key="test_api_key")
        result = client.get_glossary_entries(glossary_id="123")
        
        assert result == {"hello": "hallo", "world": "welt"}
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="GET",
            url="https://api.deepl.com/v2/glossaries/123/entries",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            params={},
            timeout=10,
        )
        
        mock_parse_glossary_entries.assert_called_once_with(
            mock_response.text, format_type="csv"
        )
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_list_glossaries(self, mock_safe_request, mock_managed_session):
        """Test that list_glossaries returns a list of glossaries."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            json_data={
                "glossaries": [
                    {
                        "glossary_id": "123",
                        "name": "My Glossary 1",
                        "source_lang": "EN",
                        "target_lang": "DE",
                        "creation_time": "2021-01-01T00:00:00Z",
                        "entry_count": 2,
                    },
                    {
                        "glossary_id": "456",
                        "name": "My Glossary 2",
                        "source_lang": "EN",
                        "target_lang": "FR",
                        "creation_time": "2021-01-02T00:00:00Z",
                        "entry_count": 3,
                    },
                ]
            }
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.list_glossaries()
        
        assert isinstance(result, GlossaryListResponse)
        assert len(result.glossaries) == 2
        assert result.glossaries[0].glossary_id == "123"
        assert result.glossaries[0].name == "My Glossary 1"
        assert result.glossaries[0].source_lang == SourceLanguage.EN
        assert result.glossaries[0].target_lang == TargetLanguage.DE
        assert result.glossaries[0].creation_time == "2021-01-01T00:00:00Z"
        assert result.glossaries[0].entry_count == 2
        assert result.glossaries[1].glossary_id == "456"
        assert result.glossaries[1].name == "My Glossary 2"
        assert result.glossaries[1].source_lang == SourceLanguage.EN
        assert result.glossaries[1].target_lang == TargetLanguage.FR
        assert result.glossaries[1].creation_time == "2021-01-02T00:00:00Z"
        assert result.glossaries[1].entry_count == 3
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="GET",
            url="https://api.deepl.com/v2/glossaries",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            timeout=10,
        )
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_delete_glossary(self, mock_safe_request, mock_managed_session):
        """Test that delete_glossary deletes a glossary."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            status_code=204,
            ok=True,
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        client.delete_glossary(glossary_id="123")
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="DELETE",
            url="https://api.deepl.com/v2/glossaries/123",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            timeout=10,
        )
    
    @patch("src.client.DeepLClient.upload_document")
    @patch("src.client.DeepLClient.wait_for_document")
    @patch("src.client.DeepLClient.download_document")
    def test_translate_document(self, mock_download_document, mock_wait_for_document, mock_upload_document):
        """Test that translate_document translates a document."""
        mock_upload_document.return_value = DocumentTranslationResponse(
            document_id="123",
            document_key="456",
        )
        
        mock_wait_for_document.return_value = DocumentTranslationStatusResponse(
            document_id="123",
            status="done",
            seconds_remaining=0,
            billed_characters=100,
        )
        
        client = DeepLClient(api_key="test_api_key")
        result = client.translate_document(
            input_file="test.txt",
            target_lang=TargetLanguage.DE,
            output_file="test_de.txt",
        )
        
        assert isinstance(result, DocumentTranslationResult)
        assert result.document_id == "123"
        assert result.document_key == "456"
        
        mock_upload_document.assert_called_once_with(
            input_file="test.txt",
            target_lang=TargetLanguage.DE,
            source_lang=None,
            formality=None,
            glossary_id=None,
        )
        
        mock_wait_for_document.assert_called_once_with(
            document_id="123",
            document_key="456",
        )
        
        mock_download_document.assert_called_once_with(
            document_id="123",
            document_key="456",
            output_file="test_de.txt",
        )
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    @patch("src.client.validate_file_size")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test")
    def test_upload_document(self, mock_file, mock_validate_file_size, mock_safe_request, mock_managed_session):
        """Test that upload_document uploads a document."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_validate_file_size.return_value = True
        
        mock_response = MockResponse(
            json_data={
                "document_id": "123",
                "document_key": "456",
            }
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.upload_document(
            input_file="test.txt",
            target_lang=TargetLanguage.DE,
        )
        
        assert isinstance(result, DocumentTranslationResponse)
        assert result.document_id == "123"
        assert result.document_key == "456"
        
        mock_validate_file_size.assert_called_once_with("test.txt")
        mock_file.assert_called_once_with("test.txt", "rb")
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="POST",
            url="https://api.deepl.com/v2/document",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            data={"target_lang": "DE"},
            files={"file": ("test.txt", mock_file.return_value)},
            timeout=10,
        )
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_get_document_status(self, mock_safe_request, mock_managed_session):
        """Test that get_document_status returns the status of a document."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            json_data={
                "document_id": "123",
                "status": "done",
                "seconds_remaining": 0,
                "billed_characters": 100,
            }
        )
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        result = client.get_document_status(
            document_id="123",
            document_key="456",
        )
        
        assert isinstance(result, DocumentTranslationStatusResponse)
        assert result.document_id == "123"
        assert result.status == "done"
        assert result.seconds_remaining == 0
        assert result.billed_characters == 100
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="GET",
            url="https://api.deepl.com/v2/document/123",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            params={"document_key": "456"},
            timeout=10,
        )
    
    @patch("src.client.DeepLClient.get_document_status")
    @patch("time.sleep")
    def test_wait_for_document_done(self, mock_sleep, mock_get_document_status):
        """Test that wait_for_document waits for a document to be done."""
        mock_get_document_status.return_value = DocumentTranslationStatusResponse(
            document_id="123",
            status="done",
            seconds_remaining=0,
            billed_characters=100,
        )
        
        client = DeepLClient(api_key="test_api_key")
        result = client.wait_for_document(
            document_id="123",
            document_key="456",
        )
        
        assert isinstance(result, DocumentTranslationStatusResponse)
        assert result.document_id == "123"
        assert result.status == "done"
        assert result.seconds_remaining == 0
        assert result.billed_characters == 100
        
        mock_get_document_status.assert_called_once_with(
            document_id="123",
            document_key="456",
        )
        
        mock_sleep.assert_not_called()
    
    @patch("src.client.DeepLClient.get_document_status")
    @patch("time.sleep")
    @patch("time.time")
    def test_wait_for_document_queued_then_done(self, mock_time, mock_sleep, mock_get_document_status):
        """Test that wait_for_document waits for a document to be done when it's queued first."""
        mock_time.side_effect = [0, 10, 20]
        
        mock_get_document_status.side_effect = [
            DocumentTranslationStatusResponse(
                document_id="123",
                status="queued",
                seconds_remaining=10,
                billed_characters=None,
            ),
            DocumentTranslationStatusResponse(
                document_id="123",
                status="done",
                seconds_remaining=0,
                billed_characters=100,
            ),
        ]
        
        client = DeepLClient(api_key="test_api_key")
        result = client.wait_for_document(
            document_id="123",
            document_key="456",
        )
        
        assert isinstance(result, DocumentTranslationStatusResponse)
        assert result.document_id == "123"
        assert result.status == "done"
        assert result.seconds_remaining == 0
        assert result.billed_characters == 100
        
        assert mock_get_document_status.call_count == 2
        mock_get_document_status.assert_has_calls([
            call(document_id="123", document_key="456"),
            call(document_id="123", document_key="456"),
        ])
        
        mock_sleep.assert_called_once_with(5)
    
    @patch("src.client.DeepLClient.get_document_status")
    @patch("time.sleep")
    @patch("time.time")
    def test_wait_for_document_error(self, mock_time, mock_sleep, mock_get_document_status):
        """Test that wait_for_document raises an exception when the document status is error."""
        mock_time.side_effect = [0, 10]
        
        mock_get_document_status.return_value = DocumentTranslationStatusResponse(
            document_id="123",
            status="error",
            seconds_remaining=None,
            billed_characters=None,
        )
        
        client = DeepLClient(api_key="test_api_key")
        
        with pytest.raises(DocumentTranslationError):
            client.wait_for_document(
                document_id="123",
                document_key="456",
            )
        
        mock_get_document_status.assert_called_once_with(
            document_id="123",
            document_key="456",
        )
        
        mock_sleep.assert_not_called()
    
    @patch("src.client.DeepLClient.get_document_status")
    @patch("time.sleep")
    @patch("time.time")
    def test_wait_for_document_timeout(self, mock_time, mock_sleep, mock_get_document_status):
        """Test that wait_for_document raises an exception when the document translation times out."""
        mock_time.side_effect = [0, 301]
        
        mock_get_document_status.return_value = DocumentTranslationStatusResponse(
            document_id="123",
            status="queued",
            seconds_remaining=10,
            billed_characters=None,
        )
        
        client = DeepLClient(api_key="test_api_key")
        
        with pytest.raises(DocumentTranslationTimeoutError):
            client.wait_for_document(
                document_id="123",
                document_key="456",
            )
        
        mock_get_document_status.assert_called_once_with(
            document_id="123",
            document_key="456",
        )
        
        mock_sleep.assert_not_called()
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_document_to_file(self, mock_file, mock_safe_request, mock_managed_session):
        """Test that download_document downloads a document to a file."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            content=b"translated content",
            ok=True,
        )
        mock_response.iter_content = MagicMock(return_value=[b"translated ", b"content"])
        mock_safe_request.return_value = mock_response
        
        client = DeepLClient(api_key="test_api_key")
        client.download_document(
            document_id="123",
            document_key="456",
            output_file="test_de.txt",
        )
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="GET",
            url="https://api.deepl.com/v2/document/123/result",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            params={"document_key": "456"},
            timeout=10,
            stream=True,
        )
        
        mock_file.assert_called_once_with("test_de.txt", "wb")
        file_handle = mock_file.return_value.__enter__.return_value
        file_handle.write.assert_has_calls([
            call(b"translated "),
            call(b"content"),
        ])
    
    @patch("src.client.managed_session")
    @patch("src.client.safe_request")
    def test_download_document_to_file_like_object(self, mock_safe_request, mock_managed_session):
        """Test that download_document downloads a document to a file-like object."""
        mock_session = MagicMock()
        mock_managed_session.return_value.__enter__.return_value = mock_session
        
        mock_response = MockResponse(
            content=b"translated content",
            ok=True,
        )
        mock_response.iter_content = MagicMock(return_value=[b"translated ", b"content"])
        mock_safe_request.return_value = mock_response
        
        mock_file = MagicMock()
        
        client = DeepLClient(api_key="test_api_key")
        client.download_document(
            document_id="123",
            document_key="456",
            output_file=mock_file,
        )
        
        mock_safe_request.assert_called_once_with(
            session=mock_session,
            method="GET",
            url="https://api.deepl.com/v2/document/123/result",
            headers={"Authorization": "DeepL-Auth-Key test_api_key"},
            params={"document_key": "456"},
            timeout=10,
            stream=True,
        )
        
        mock_file.write.assert_has_calls([
            call(b"translated "),
            call(b"content"),
        ])
    
    @patch("src.client.clean_memory_resources")
    def test_close(self, mock_clean_memory_resources):
        """Test that close cleans up resources."""
        client = DeepLClient(api_key="test_api_key")
        client.close()
        
        mock_clean_memory_resources.assert_called_once()
    
    @patch("src.client.clean_memory_resources")
    def test_context_manager(self, mock_clean_memory_resources):
        """Test that the client can be used as a context manager."""
        with DeepLClient(api_key="test_api_key") as client:
            assert isinstance(client, DeepLClient)
        
        mock_clean_memory_resources.assert_called_once()
