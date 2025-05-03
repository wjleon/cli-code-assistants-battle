"""
Integration tests for the DeepL translation API.

Note: These tests require a valid DeepL API key to be set in the DEEPL_API_KEY environment variable.
They will make actual API calls to the DeepL service, which will count against your quota.
"""
import os
import unittest
from typing import List

from deepl.client import DeepLClient
from deepl.exceptions.api_exceptions import DeepLAPIError


@unittest.skipIf(not os.environ.get("DEEPL_API_KEY"), "DEEPL_API_KEY not set in environment")
class TestTranslationIntegration(unittest.TestCase):
    """Integration tests for translation functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.client = DeepLClient()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        cls.client.close()

    def test_translate_single_text(self):
        """Test translating a single text string."""
        text = "Hello, world!"
        result = self.client.translate(text, target_lang="DE")
        
        self.assertEqual(len(result.translations), 1)
        self.assertEqual(result.translations[0].detected_source_language, "EN")
        self.assertIsInstance(result.translations[0].text, str)
        self.assertTrue(len(result.translations[0].text) > 0)
        
    def test_translate_multiple_texts(self):
        """Test translating multiple text strings."""
        texts = ["Hello, world!", "How are you?"]
        result = self.client.translate(texts, target_lang="FR")
        
        self.assertEqual(len(result.translations), 2)
        self.assertEqual(result.translations[0].detected_source_language, "EN")
        self.assertEqual(result.translations[1].detected_source_language, "EN")
        self.assertTrue(all(len(t.text) > 0 for t in result.translations))
        
    def test_translate_with_source_lang(self):
        """Test translating with explicit source language."""
        text = "Hello, world!"
        result = self.client.translate(text, source_lang="EN", target_lang="ES")
        
        self.assertEqual(len(result.translations), 1)
        self.assertEqual(result.translations[0].detected_source_language, "EN")
        self.assertIsInstance(result.translations[0].text, str)
        self.assertTrue(len(result.translations[0].text) > 0)
        
    def test_translate_with_formality(self):
        """Test translating with formality option."""
        text = "How are you?"
        
        # Translate with less formality
        result_less = self.client.translate(text, target_lang="DE", formality="less")
        
        # Translate with more formality
        result_more = self.client.translate(text, target_lang="DE", formality="more")
        
        # The translations should be different
        self.assertNotEqual(
            result_less.translations[0].text, 
            result_more.translations[0].text,
            "Formality setting did not affect translation"
        )


@unittest.skipIf(not os.environ.get("DEEPL_API_KEY"), "DEEPL_API_KEY not set in environment")
class TestLanguagesIntegration(unittest.TestCase):
    """Integration tests for languages functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.client = DeepLClient()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        cls.client.close()

    def test_get_source_languages(self):
        """Test getting source languages."""
        languages = self.client.get_languages(type="source")
        
        self.assertIsInstance(languages, List)
        self.assertTrue(len(languages) > 0)
        
        # Check that English is in the list
        self.assertTrue(any(lang.language == "EN" for lang in languages))
        
    def test_get_target_languages(self):
        """Test getting target languages."""
        languages = self.client.get_languages(type="target")
        
        self.assertIsInstance(languages, List)
        self.assertTrue(len(languages) > 0)
        
        # Check that German is in the list
        self.assertTrue(any(lang.language == "DE" for lang in languages))
        
        # Check formality support
        german = next(lang for lang in languages if lang.language == "DE")
        self.assertTrue(german.supports_formality)
        
    def test_get_supported_languages(self):
        """Test getting all supported languages."""
        supported_languages = self.client.get_supported_languages()
        
        self.assertTrue(len(supported_languages.source) > 0)
        self.assertTrue(len(supported_languages.target) > 0)


@unittest.skipIf(not os.environ.get("DEEPL_API_KEY"), "DEEPL_API_KEY not set in environment")
class TestUsageIntegration(unittest.TestCase):
    """Integration tests for usage functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.client = DeepLClient()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        cls.client.close()

    def test_get_usage(self):
        """Test getting usage information."""
        usage = self.client.get_usage()
        
        self.assertIsInstance(usage.character_count, int)
        # character_limit might be None for unlimited plans
        if usage.character_limit is not None:
            self.assertIsInstance(usage.character_limit, int)
            self.assertGreaterEqual(usage.character_limit, usage.character_count)


if __name__ == "__main__":
    unittest.main()