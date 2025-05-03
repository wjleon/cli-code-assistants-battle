#!/usr/bin/env python3
"""
Demo script for DeepL API integration.

This script demonstrates the translation of a Spanish text to English, Ukrainian, and Italian
using the DeepL API client.
"""

import os
import sys
from typing import Dict, List, Optional

from src.client import DeepLClient
from src.models import TargetLanguage
from src.exceptions import DeepLError, AuthenticationError


def print_colored(text: str, color: str = "default") -> None:
    """
    Print colored text to the console.
    
    Args:
        text: The text to print.
        color: The color to use. One of "red", "green", "yellow", "blue", "magenta", "cyan", or "default".
    """
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "default": "\033[0m",
    }
    
    color_code = colors.get(color.lower(), colors["default"])
    reset_code = colors["default"]
    
    print(f"{color_code}{text}{reset_code}")


def print_translation_result(language: str, text: str) -> None:
    """
    Print a translation result with formatting.
    
    Args:
        language: The language name.
        text: The translated text.
    """
    print_colored(f"\n{language} Translation:", "blue")
    print_colored(f"  {text}", "green")


def main() -> int:
    """
    Main function to demonstrate the DeepL API client.
    
    Returns:
        Exit code. 0 for success, non-zero for failure.
    """
    # Check if the API key is set
    if "DEEPL_API_KEY" not in os.environ:
        print_colored(
            "Error: DEEPL_API_KEY environment variable not set. "
            "Please set it to your DeepL API key.",
            "red",
        )
        return 1
    
    # The text to translate
    original_text = "Un Saludos a mis queridos colegas de IOL"
    
    print_colored("DeepL API Translation Demo", "magenta")
    print_colored("===========================\n", "magenta")
    
    print_colored("Original Text (Spanish):", "blue")
    print_colored(f"  {original_text}", "cyan")
    
    try:
        # Create a DeepL client
        client = DeepLClient()
        
        # Target languages to translate to
        target_languages = [
            ("English", TargetLanguage.EN),
            ("Ukrainian", TargetLanguage.UK),
            ("Italian", TargetLanguage.IT),
        ]
        
        # Translate the text to each target language
        for language_name, language_code in target_languages:
            try:
                # Translate the text
                result = client.translate_text(
                    text=original_text,
                    target_lang=language_code,
                )
                
                # Print the translation
                if result.translations:
                    translated_text = result.translations[0].text
                    print_translation_result(language_name, translated_text)
                else:
                    print_colored(
                        f"\nWarning: No translation returned for {language_name}.",
                        "yellow",
                    )
            except DeepLError as e:
                print_colored(
                    f"\nError translating to {language_name}: {str(e)}",
                    "red",
                )
        
        print_colored("\nTranslation demo completed successfully!", "magenta")
        return 0
    
    except AuthenticationError as e:
        print_colored(f"Authentication error: {str(e)}", "red")
        return 1
    except DeepLError as e:
        print_colored(f"DeepL API error: {str(e)}", "red")
        return 1
    except Exception as e:
        print_colored(f"Unexpected error: {str(e)}", "red")
        return 1
    finally:
        # Clean up resources
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    sys.exit(main())
