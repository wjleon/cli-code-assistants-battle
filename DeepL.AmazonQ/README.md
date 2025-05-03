# DeepL API Integration

This repository contains a Python integration for the DeepL Translation API. It provides a clean, modular, and reusable interface to interact with DeepL's translation services.

## Project Structure

```
.
├── README.md                 # Project documentation
├── deepl_integration/        # Main package
│   ├── __init__.py           # Package initialization
│   ├── client.py             # DeepL API client
│   ├── models.py             # Data models
│   ├── exceptions.py         # Custom exceptions
│   └── utils.py              # Utility functions
├── tests/                    # Test directory
│   ├── unit/                 # Unit tests
│   │   ├── __init__.py
│   │   ├── test_client.py
│   │   ├── test_models.py
│   │   └── test_utils.py
│   └── integration/          # Integration tests
│       ├── __init__.py
│       └── test_translation.py
└── demo.py                   # Demo application
```

## Features

- Secure API key handling via environment variables
- Comprehensive error handling
- Full test coverage (unit and integration tests)
- Clean, modular design following SOLID principles
- Proper documentation

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd deepl-integration

# Install dependencies
pip install -r requirements.txt
```

## Usage

Set your DeepL API key as an environment variable:

```bash
export DEEPL_API_KEY="your-api-key"
```

Basic usage example:

```python
from deepl_integration.client import DeepLClient

# Create a client instance
client = DeepLClient()

# Translate text
result = client.translate("Hello, world!", target_lang="DE")
print(result.text)  # "Hallo, Welt!"
```

See `demo.py` for more examples.

## Testing

Run the tests with:

```bash
# Run unit tests
pytest tests/unit

# Run integration tests (requires valid API key)
pytest tests/integration

# Run all tests
pytest
```

## License

[MIT License](LICENSE)
