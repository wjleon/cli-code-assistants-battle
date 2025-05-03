#!/usr/bin/env python3
"""
Demo script for DeepLClient usage.
Translates a sample text into English, Ukrainian, and Italian.
"""

import sys

from deepl_translator.client import DeepLClient
from deepl_translator.exceptions import MissingAPIKeyException, DeepLException

def main():
    try:
        client = DeepLClient()
    except MissingAPIKeyException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    text = "Un Saludos a mis queridos colegas de IOL"
    target_languages = {
        "EN": "English",
        "UK": "Ukrainian",
        "IT": "Italian"
    }

    for code, name in target_languages.items():
        try:
            translation = client.translate(text, target_language=code)
            print(f"{name} ({code}): {translation}")
        except DeepLException as e:
            print(f"Failed to translate to {name} ({code}): {e}", file=sys.stderr)

if __name__ == "__main__":
    main()