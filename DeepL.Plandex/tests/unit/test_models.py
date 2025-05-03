"""
Unit tests for the models module.
"""

import pytest
from pydantic import ValidationError

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


class TestEnums:
    """Tests for the enum models."""

    def test_source_language_values(self):
        """Test that SourceLanguage enum has the expected values."""
        assert SourceLanguage.AUTO == "auto"
        assert SourceLanguage.EN == "EN"
        assert SourceLanguage.DE == "DE"
        assert SourceLanguage.FR == "FR"

    def test_target_language_values(self):
        """Test that TargetLanguage enum has the expected values."""
        assert TargetLanguage.EN == "EN"
        assert TargetLanguage.EN_GB == "EN-GB"
        assert TargetLanguage.EN_US == "EN-US"
        assert TargetLanguage.DE == "DE"

    def test_formality_values(self):
        """Test that Formality enum has the expected values."""
        assert Formality.DEFAULT == "default"
        assert Formality.MORE == "more"
        assert Formality.LESS == "less"

    def test_split_sentences_values(self):
        """Test that SplitSentences enum has the expected values."""
        assert SplitSentences.OFF == "0"
        assert SplitSentences.ON == "1"
        assert SplitSentences.NO_NEWLINES == "nonewlines"

    def test_preserve_formatting_values(self):
        """Test that PreserveFormatting enum has the expected values."""
        assert PreserveFormatting.OFF == "0"
        assert PreserveFormatting.ON == "1"

    def test_tag_handling_values(self):
        """Test that TagHandling enum has the expected values."""
        assert TagHandling.XML == "xml"
        assert TagHandling.HTML == "html"

    def test_outline_detection_values(self):
        """Test that OutlineDetection enum has the expected values."""
        assert OutlineDetection.OFF == "0"
        assert OutlineDetection.ON == "1"

    def test_glossary_format_values(self):
        """Test that GlossaryFormat enum has the expected values."""
        assert GlossaryFormat.CSV == "csv"
        assert GlossaryFormat.TSV == "tsv"


class TestTextTranslationRequest:
    """Tests for the TextTranslationRequest model."""

    def test_valid_request_with_string_text(self):
        """Test that a valid request with string text is accepted."""
        request = TextTranslationRequest(
            text="Hello, world!",
            target_lang=TargetLanguage.DE,
        )
        assert request.text == "Hello, world!"
        assert request.target_lang == TargetLanguage.DE
        assert request.source_lang == SourceLanguage.AUTO
        assert request.split_sentences == SplitSentences.ON
        assert request.preserve_formatting == PreserveFormatting.OFF
        assert request.formality == Formality.DEFAULT
        assert request.glossary_id is None
        assert request.tag_handling is None
        assert request.outline_detection == OutlineDetection.ON
        assert request.non_splitting_tags is None
        assert request.splitting_tags is None
        assert request.ignore_tags is None

    def test_valid_request_with_list_text(self):
        """Test that a valid request with list text is accepted."""
        request = TextTranslationRequest(
            text=["Hello, world!", "How are you?"],
            target_lang=TargetLanguage.DE,
        )
        assert request.text == ["Hello, world!", "How are you?"]
        assert request.target_lang == TargetLanguage.DE

    def test_valid_request_with_all_parameters(self):
        """Test that a valid request with all parameters is accepted."""
        request = TextTranslationRequest(
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
        assert request.text == "Hello, world!"
        assert request.target_lang == TargetLanguage.DE
        assert request.source_lang == SourceLanguage.EN
        assert request.split_sentences == SplitSentences.OFF
        assert request.preserve_formatting == PreserveFormatting.ON
        assert request.formality == Formality.MORE
        assert request.glossary_id == "123"
        assert request.tag_handling == TagHandling.XML
        assert request.outline_detection == OutlineDetection.OFF
        assert request.non_splitting_tags == ["p", "div"]
        assert request.splitting_tags == ["br"]
        assert request.ignore_tags == ["span"]

    def test_invalid_request_with_empty_text(self):
        """Test that a request with empty text is rejected."""
        with pytest.raises(ValidationError):
            TextTranslationRequest(
                text="",
                target_lang=TargetLanguage.DE,
            )

    def test_invalid_request_with_empty_list(self):
        """Test that a request with an empty list is rejected."""
        with pytest.raises(ValidationError):
            TextTranslationRequest(
                text=[],
                target_lang=TargetLanguage.DE,
            )

    def test_invalid_request_with_list_of_empty_strings(self):
        """Test that a request with a list of empty strings is rejected."""
        with pytest.raises(ValidationError):
            TextTranslationRequest(
                text=["", ""],
                target_lang=TargetLanguage.DE,
            )

    def test_to_api_params_with_string_text(self):
        """Test that to_api_params returns the correct parameters with string text."""
        request = TextTranslationRequest(
            text="Hello, world!",
            target_lang=TargetLanguage.DE,
        )
        params = request.to_api_params()
        assert params["text"] == "Hello, world!"
        assert params["target_lang"] == "DE"
        assert "source_lang" not in params

    def test_to_api_params_with_list_text(self):
        """Test that to_api_params returns the correct parameters with list text."""
        request = TextTranslationRequest(
            text=["Hello, world!", "How are you?"],
            target_lang=TargetLanguage.DE,
        )
        params = request.to_api_params()
        assert params["text=0"] == "Hello, world!"
        assert params["text=1"] == "How are you?"
        assert params["target_lang"] == "DE"

    def test_to_api_params_with_all_parameters(self):
        """Test that to_api_params returns the correct parameters with all parameters."""
        request = TextTranslationRequest(
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
        params = request.to_api_params()
        assert params["text"] == "Hello, world!"
        assert params["target_lang"] == "DE"
        assert params["source_lang"] == "EN"
        assert params["split_sentences"] == "0"
        assert params["preserve_formatting"] == "1"
        assert params["formality"] == "more"
        assert params["glossary_id"] == "123"
        assert params["tag_handling"] == "xml"
        assert params["outline_detection"] == "0"
        assert params["non_splitting_tags"] == "p,div"
        assert params["splitting_tags"] == "br"
        assert params["ignore_tags"] == "span"


class TestTextTranslationResponse:
    """Tests for the TextTranslationResponse model."""

    def test_valid_response(self):
        """Test that a valid response is accepted."""
        response = TextTranslationResponse(
            translations=[
                TranslatedText(
                    text="Hallo, Welt!",
                    detected_source_language=SourceLanguage.EN,
                )
            ]
        )
        assert len(response.translations) == 1
        assert response.translations[0].text == "Hallo, Welt!"
        assert response.translations[0].detected_source_language == SourceLanguage.EN

    def test_valid_response_with_multiple_translations(self):
        """Test that a valid response with multiple translations is accepted."""
        response = TextTranslationResponse(
            translations=[
                TranslatedText(
                    text="Hallo, Welt!",
                    detected_source_language=SourceLanguage.EN,
                ),
                TranslatedText(
                    text="Wie geht es dir?",
                    detected_source_language=SourceLanguage.EN,
                ),
            ]
        )
        assert len(response.translations) == 2
        assert response.translations[0].text == "Hallo, Welt!"
        assert response.translations[0].detected_source_language == SourceLanguage.EN
        assert response.translations[1].text == "Wie geht es dir?"
        assert response.translations[1].detected_source_language == SourceLanguage.EN


class TestGlossaryCreateRequest:
    """Tests for the GlossaryCreateRequest model."""

    def test_valid_request_with_string_entries(self):
        """Test that a valid request with string entries is accepted."""
        request = GlossaryCreateRequest(
            name="My Glossary",
            source_lang=SourceLanguage.EN,
            target_lang=TargetLanguage.DE,
            entries="hello,hallo\nworld,welt",
        )
        assert request.name == "My Glossary"
        assert request.source_lang == SourceLanguage.EN
        assert request.target_lang == TargetLanguage.DE
        assert request.entries == "hello,hallo\nworld,welt"
        assert request.entries_format == GlossaryFormat.CSV

    def test_invalid_request_with_empty_name(self):
        """Test that a request with an empty name is rejected."""
        with pytest.raises(ValidationError):
            GlossaryCreateRequest(
                name="",
                source_lang=SourceLanguage.EN,
                target_lang=TargetLanguage.DE,
                entries="hello,hallo\nworld,welt",
            )

    def test_invalid_request_with_empty_entries(self):
        """Test that a request with empty entries is rejected."""
        with pytest.raises(ValidationError):
            GlossaryCreateRequest(
                name="My Glossary",
                source_lang=SourceLanguage.EN,
                target_lang=TargetLanguage.DE,
                entries="",
            )


class TestDocumentTranslationRequest:
    """Tests for the DocumentTranslationRequest model."""

    def test_valid_request(self):
        """Test that a valid request is accepted."""
        request = DocumentTranslationRequest(
            target_lang=TargetLanguage.DE,
        )
        assert request.target_lang == TargetLanguage.DE
        assert request.source_lang == SourceLanguage.AUTO
        assert request.formality == Formality.DEFAULT
        assert request.glossary_id is None

    def test_valid_request_with_all_parameters(self):
        """Test that a valid request with all parameters is accepted."""
        request = DocumentTranslationRequest(
            target_lang=TargetLanguage.DE,
            source_lang=SourceLanguage.EN,
            formality=Formality.MORE,
            glossary_id="123",
        )
        assert request.target_lang == TargetLanguage.DE
        assert request.source_lang == SourceLanguage.EN
        assert request.formality == Formality.MORE
        assert request.glossary_id == "123"
