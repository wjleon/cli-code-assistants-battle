"""
Unit tests for the DeepL API models.
"""
import unittest
from pydantic import ValidationError as PydanticValidationError

from deepl.models.translation import TranslationRequest, Translation, TranslationResponse
from deepl.models.language import Language, SupportedLanguages
from deepl.models.usage import Usage


class TestTranslationModels(unittest.TestCase):
    """Test cases for translation models."""

    def test_translation_request_valid(self):
        """Test creating a valid TranslationRequest."""
        # Test with string
        request = TranslationRequest(text="Hello, world!", target_lang="de")
        self.assertEqual(request.text, "Hello, world!")
        self.assertEqual(request.target_lang, "DE")
        self.assertIsNone(request.source_lang)
        
        # Test with list of strings
        request = TranslationRequest(
            text=["Hello, world!", "Test"],
            target_lang="de",
            source_lang="en"
        )
        self.assertEqual(request.text, ["Hello, world!", "Test"])
        self.assertEqual(request.target_lang, "DE")
        self.assertEqual(request.source_lang, "EN")
        
        # Test with additional parameters
        request = TranslationRequest(
            text="Hello, world!",
            target_lang="de",
            source_lang="en",
            formality="more",
            preserve_formatting=True
        )
        self.assertEqual(request.formality, "more")
        self.assertTrue(request.preserve_formatting)
        
    def test_translation_request_invalid(self):
        """Test creating invalid TranslationRequest."""
        # Test with empty text
        with self.assertRaises(PydanticValidationError):
            TranslationRequest(text="", target_lang="de")
            
        # Test with empty list
        with self.assertRaises(PydanticValidationError):
            TranslationRequest(text=[], target_lang="de")
            
        # Test with list of empty strings
        with self.assertRaises(PydanticValidationError):
            TranslationRequest(text=["", "  "], target_lang="de")
            
        # Test missing required field
        with self.assertRaises(PydanticValidationError):
            TranslationRequest(text="Hello")
            
    def test_translation_request_to_api_request(self):
        """Test converting TranslationRequest to API format."""
        request = TranslationRequest(
            text="Hello, world!",
            target_lang="de",
            source_lang="en",
            formality="more"
        )
        api_request = request.to_api_request()
        
        self.assertEqual(api_request["text"], "Hello, world!")
        self.assertEqual(api_request["target_lang"], "DE")
        self.assertEqual(api_request["source_lang"], "EN")
        self.assertEqual(api_request["formality"], "more")
        
    def test_translation_model(self):
        """Test Translation model."""
        translation = Translation(
            detected_source_language="EN",
            text="Hallo, Welt!"
        )
        self.assertEqual(translation.detected_source_language, "EN")
        self.assertEqual(translation.text, "Hallo, Welt!")
        
    def test_translation_response_model(self):
        """Test TranslationResponse model."""
        response = TranslationResponse(
            translations=[
                {
                    "detected_source_language": "EN",
                    "text": "Hallo, Welt!"
                },
                {
                    "detected_source_language": "EN",
                    "text": "Test"
                }
            ]
        )
        
        self.assertEqual(len(response.translations), 2)
        self.assertEqual(response.translations[0].detected_source_language, "EN")
        self.assertEqual(response.translations[0].text, "Hallo, Welt!")
        self.assertEqual(response.translations[1].text, "Test")


class TestLanguageModels(unittest.TestCase):
    """Test cases for language models."""
    
    def test_language_model(self):
        """Test Language model."""
        # Basic language
        lang = Language(language="EN", name="English")
        self.assertEqual(lang.language, "EN")
        self.assertEqual(lang.name, "English")
        self.assertFalse(lang.supports_formality)
        
        # Language with formality support
        lang = Language(language="DE", name="German", supports_formality=True)
        self.assertEqual(lang.language, "DE")
        self.assertEqual(lang.name, "German")
        self.assertTrue(lang.supports_formality)
        
    def test_supported_languages_model(self):
        """Test SupportedLanguages model."""
        # Empty lists
        langs = SupportedLanguages()
        self.assertEqual(langs.source, [])
        self.assertEqual(langs.target, [])
        
        # With languages
        langs = SupportedLanguages(
            source=[
                Language(language="EN", name="English"),
                Language(language="DE", name="German")
            ],
            target=[
                Language(language="FR", name="French"),
                Language(language="ES", name="Spanish")
            ]
        )
        
        self.assertEqual(len(langs.source), 2)
        self.assertEqual(langs.source[0].language, "EN")
        self.assertEqual(langs.source[1].name, "German")
        
        self.assertEqual(len(langs.target), 2)
        self.assertEqual(langs.target[0].language, "FR")
        self.assertEqual(langs.target[1].name, "Spanish")


class TestUsageModel(unittest.TestCase):
    """Test cases for usage model."""
    
    def test_usage_model(self):
        """Test Usage model."""
        # With limit
        usage = Usage(character_count=100000, character_limit=1000000)
        self.assertEqual(usage.character_count, 100000)
        self.assertEqual(usage.character_limit, 1000000)
        self.assertEqual(usage.character_percentage, 10.0)
        
        # Without limit
        usage = Usage(character_count=100000, character_limit=None)
        self.assertEqual(usage.character_count, 100000)
        self.assertIsNone(usage.character_limit)
        self.assertIsNone(usage.character_percentage)
        
        # Zero limit (avoid division by zero)
        usage = Usage(character_count=100000, character_limit=0)
        self.assertIsNone(usage.character_percentage)


if __name__ == "__main__":
    unittest.main()