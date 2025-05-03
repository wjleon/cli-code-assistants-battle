# DeepL API Python Client

A comprehensive Python client for the DeepL Translation API, following best software development practices including SOLID principles, DRY, and KISS.

## Features

- Text translation with support for all DeepL API features
- Language detection and language listing
- Usage tracking and quota management
- Robust error handling and logging
- Comprehensive test coverage
- Clean, modular, and documented codebase

## Installation

### Requirements

- Python 3.8 or higher
- A valid DeepL API key (get one at [DeepL API](https://www.deepl.com/pro-api))

### Install from Source

```bash
git clone https://github.com/yourusername/deepl-api-python.git
cd deepl-api-python
pip install -e .
```

## Quick Start

```python
import os
from deepl.client import DeepLClient

# Set your API key in the environment
os.environ["DEEPL_API_KEY"] = "your-api-key"

# Create a client
client = DeepLClient()

# Translate text
result = client.translate("Hello, world!", target_lang="DE")
print(result.translations[0].text)  # "Hallo, Welt!"

# Close the client when done
client.close()

# Or use as a context manager
with DeepLClient() as client:
    result = client.translate("Hello, world!", target_lang="FR")
    print(result.translations[0].text)
```

## Repository Structure

```
deepl_api/
├── docs/                  # Documentation files
├── src/                   # Source code
│   └── deepl/             # Main package
│       ├── __init__.py    # Package exports
│       ├── client.py      # DeepL API client
│       ├── exceptions/    # Error handling
│       │   └── api_exceptions.py  # API-specific exceptions
│       └── models/        # Data models
│           ├── language.py       # Language models
│           ├── translation.py    # Translation models
│           └── usage.py          # Usage models
├── tests/                 # Test suite
│   ├── integration/       # Integration tests
│   │   └── test_translation.py
│   └── unit/              # Unit tests
│       ├── test_client.py
│       ├── test_exceptions.py
│       └── test_models.py
├── demo.py                # Demo script
├── setup.py               # Package setup script
├── pyproject.toml         # Build system configuration
└── README.md              # This file
```

## API Usage

### Translation

```python
from deepl.client import DeepLClient

client = DeepLClient()

# Simple translation
result = client.translate("Hello, world!", target_lang="DE")

# Translate multiple texts at once
result = client.translate(
    ["Hello, world!", "How are you?"], 
    target_lang="FR"
)

# Specify source language
result = client.translate(
    "Hello, world!",
    source_lang="EN",
    target_lang="ES"
)

# Set formality level
result = client.translate(
    "How are you?",
    target_lang="DE",
    formality="more"  # or "less"
)

# Handle HTML content
result = client.translate(
    "<p>Hello, <b>world</b>!</p>",
    target_lang="DE",
    tag_handling="html"
)

client.close()
```

### Language Management

```python
from deepl.client import DeepLClient

client = DeepLClient()

# Get source languages
source_languages = client.get_languages(type="source")

# Get target languages
target_languages = client.get_languages(type="target")

# Get all supported languages
all_languages = client.get_supported_languages()

client.close()
```

### Usage Information

```python
from deepl.client import DeepLClient

client = DeepLClient()

# Get usage statistics
usage = client.get_usage()
print(f"Characters used: {usage.character_count}")
print(f"Character limit: {usage.character_limit}")
print(f"Usage percentage: {usage.character_percentage:.2f}%")

client.close()
```

## Testing

### Running Unit Tests

```bash
python -m unittest discover -s tests/unit
```

### Running Integration Tests

```bash
# Set your API key for integration tests
export DEEPL_API_KEY="your-api-key"

python -m unittest discover -s tests/integration
```

## Demo Script

A demonstration script is included in the repository. Run it with:

```bash
# Set your API key
export DEEPL_API_KEY="your-api-key"

# Run the demo
python demo.py
```

The demo translates a Spanish greeting to English, Ukrainian, and Hindi.

## Error Handling

The client includes comprehensive error handling for various API error scenarios:

```python
from deepl.client import DeepLClient
from deepl.exceptions.api_exceptions import DeepLAPIError, AuthorizationError, QuotaExceededError

client = DeepLClient()

try:
    result = client.translate("Hello, world!", target_lang="DE")
    print(result.translations[0].text)
except AuthorizationError as e:
    print(f"Authentication failed: {e}")
except QuotaExceededError as e:
    print(f"Quota exceeded: {e}")
except DeepLAPIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    client.close()
```

## Best Practices

This implementation follows these software development best practices:

1. **SOLID Principles**:
   - Single Responsibility: Each class has a single responsibility
   - Open/Closed: Code is open for extension but closed for modification
   - Liskov Substitution: Derived exceptions can be used in place of base exceptions
   - Interface Segregation: Clean API separates concerns
   - Dependency Inversion: High-level modules depend on abstractions

2. **DRY (Don't Repeat Yourself)**:
   - Common functionality is abstracted
   - Base classes handle shared behavior

3. **KISS (Keep It Simple, Stupid)**:
   - Clean, straightforward API design
   - Intuitive method names and parameters

4. **Security**:
   - Environment variable for API key
   - No hardcoded secrets
   - Proper exception handling to avoid leaking sensitive information

5. **Memory Management**:
   - Resources properly closed with context manager support
   - No memory leaks

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- DeepL for providing an excellent translation API
- The open-source community for inspiration

## Future Plans

Features planned for future releases:

- Document translation support
- Text improvement capabilities
- Glossary management
- More extensive CLI tools
- Additional language-specific features