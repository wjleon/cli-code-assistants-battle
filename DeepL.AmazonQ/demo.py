#!/usr/bin/env python3
"""
Demo application for the DeepL API integration.

This script demonstrates how to use the DeepL API client to translate text
into multiple languages.
"""

import os
import sys
from typing import List

from deepl_integration.client import DeepLClient
from deepl_integration.exceptions import DeepLError


def translate_to_languages(text: str, target_languages: List[str]) -> None:
    """
    Translate text to multiple languages.
    
    Args:
        text: The text to translate.
        target_languages: List of target language codes.
    """
    try:
        # Create a client instance
        client = DeepLClient(is_pro=True)
        
        print(f"Original text: {text}")
        print("-" * 50)
        
        # Translate to each target language
        for lang in target_languages:
            try:
                result = client.translate(text, target_lang=lang)
                print(f"{lang}: {result.text}")
                print(f"Detected source language: {result.detected_source_language}")
                print("-" * 50)
            except DeepLError as e:
                print(f"Error translating to {lang}: {str(e)}")
        
        # Get usage information
        try:
            usage = client.get_usage_information()
            print(f"API Usage: {usage.character_count} / {usage.character_limit} characters")
            print(f"Usage percentage: {usage.character_percentage:.2f}%")
        except DeepLError as e:
            print(f"Error getting usage information: {str(e)}")
            
    except DeepLError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def main() -> None:
    """Main function."""
    # Check if API key is set
    if not os.environ.get("DEEPL_API_KEY"):
        print("Error: DEEPL_API_KEY environment variable not set.")
        print("Please set it with: export DEEPL_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Text to translate
    text = "Un Saludos a mis queridos colegas de IOL"
    
    # Target languages
    target_languages = ["EN", "UK", "IT"]
    
    # Translate
    translate_to_languages(text, target_languages)


if __name__ == "__main__":
    main()
