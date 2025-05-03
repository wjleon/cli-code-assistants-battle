#!/usr/bin/env python3
"""
Demo script for the DeepL API client.

This script demonstrates how to use the DeepL API client to translate text
to multiple languages.

Requirements:
- DEEPL_API_KEY environment variable must be set with a valid DeepL API key
"""
import os
import sys
from typing import List, Dict
from pprint import pprint

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_path)

# Import DeepL client
from deepl.client import DeepLClient
from deepl.exceptions.api_exceptions import DeepLAPIError


def translate_to_languages(text: str, target_languages: List[str]) -> Dict[str, str]:
    """
    Translate text to multiple languages.
    
    Args:
        text: Text to translate
        target_languages: List of target language codes
        
    Returns:
        Dictionary mapping language codes to translated text
    """
    # Check if API key is set
    if not os.environ.get("DEEPL_API_KEY"):
        print("Error: DEEPL_API_KEY environment variable not set")
        print("Please set the DEEPL_API_KEY environment variable with your DeepL API key")
        sys.exit(1)
    
    results = {}
    
    # Create DeepL client
    client = DeepLClient()
    
    try:
        print(f"Translating: \"{text}\"")
        print("Target languages:", ", ".join(target_languages))
        print("\nResults:")
        print("-" * 50)
        
        # Translate to each target language
        for lang in target_languages:
            try:
                response = client.translate(text, target_lang=lang)
                translated_text = response.translations[0].text
                results[lang] = translated_text
                print(f"{lang}: {translated_text}")
            except DeepLAPIError as e:
                print(f"Error translating to {lang}: {e}")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the client to release resources
        client.close()
    
    return results


def main():
    """Main function."""
    # Print supported languages
    try:
        print("Getting supported languages...")
        client = DeepLClient()
        languages = client.get_supported_languages()
        
        print("\nSupported Target Languages:")
        for lang in languages.target:
            print(f"- {lang.language}: {lang.name}")
        print()
        client.close()
    except Exception as e:
        print(f"Error getting supported languages: {e}")
        print()
    
    # Text to translate
    text = "Un Saludos a mis queridos colegas de IOL"
    
    # Target languages (English, Ukrainian, French) - HI (Hindi) is not supported
    target_languages = ["EN", "UK", "FR"]
    
    # Translate the text
    translations = translate_to_languages(text, target_languages)
    
    # Print usage information
    try:
        client = DeepLClient()
        usage = client.get_usage()
        print("\nDeepL API Usage:")
        print(f"Characters used: {usage.character_count:,}")
        if usage.character_limit:
            print(f"Character limit: {usage.character_limit:,}")
            print(f"Usage percentage: {usage.character_percentage:.2f}%")
        else:
            print("Character limit: Unlimited")
        client.close()
    except Exception as e:
        print(f"Error getting usage information: {e}")


if __name__ == "__main__":
    main()