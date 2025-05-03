# DeepL API Integration

A Python client for the DeepL API that follows best practices for security, memory management, and software design.

## Features

- Secure API key handling via environment variables
- Complete implementation of all DeepL API endpoints
- Proper error handling and resource management
- Comprehensive test suite
- Type hints for better IDE support
- Follows SOLID principles, DRY, and KISS

## Installation

```bash
pip install -e .
```

## Usage

### Basic Translation

```python
import os
from deepl_integration import DeepLClient

# Set your API key as an environment variable
os.environ["DEEPL_API_KEY"] = "your-api-key"

# Create a client
client = DeepLClient()

# Translate text
result = client.translate_text(
    text="Hello, world!",
    source_lang="EN",
    target_lang="DE"
)

print(result.text)  # "Hallo, Welt!"
```

### Supported Languages

The client supports all languages offered by the DeepL API:

- English (EN)
- German (DE)
- French (FR)
- Spanish (ES)
- Portuguese (PT)
- Italian (IT)
- Dutch (NL)
- Polish (PL)
- Russian (RU)
- Japanese (JA)
- Chinese (ZH)
- And more...

### Advanced Usage

For more advanced usage, including document translation and glossary management, see the examples in the documentation.

## Project Structure

```
deepl_integration/
├── src/
│   ├── __init__.py         # Package initialization
│   ├── client.py           # Main DeepL client
│   ├── models.py           # Data models
│   ├── exceptions.py       # Custom exceptions
│   ├── config.py           # Configuration handling
│   └── utils.py            # Utility functions
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── demo.py                 # Demo script
├── README.md               # This file
├── requirements.txt        # Dependencies
└── setup.py                # Package setup
```

## Development

### Setting Up Development Environment

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install development dependencies: `pip install -e ".[dev]"`

### Running Tests

```bash
pytest tests/unit/
```

To run integration tests (requires a valid DeepL API key):

```bash
pytest tests/integration/
```

## Security Considerations

- The API key is read from the environment variable `DEEPL_API_KEY`
- All API requests are made over HTTPS
- Input validation is performed before sending requests
- Error messages are sanitized to prevent information leakage

## License

MIT
