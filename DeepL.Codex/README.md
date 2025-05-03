# DeepL Translator Python Integration

This repository provides a modular and reusable Python client for the [DeepL API](https://www.deepl.com/docs).

## Repository Structure

- `deepl_translator/`
  - `client.py`: Main client class (`DeepLClient`) for interacting with the DeepL API.
  - `exceptions.py`: Custom exception classes for error handling.
  - `__init__.py`: Package metadata.
- `tests/`
  - `unit/`
    - `test_client.py`: Unit tests with mocked HTTP responses.
  - `integration/`
    - `test_integration_client.py`: Integration tests against the real DeepL API.
- `demo.py`: Demonstration script translating a sample text into English, Ukrainian, and Italian.
- `README.md`: This file.

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install requests pytest requests-mock
   ```

## Environment Variables

- `DEEPL_API_KEY`: Your DeepL API authentication key. Must be set to run the client or integration tests.

## Usage

```python
from deepl_translator.client import DeepLClient

client = DeepLClient()  # reads API key from DEEPL_API_KEY
translated = client.translate("Hello, world!", target_language="DE")
print(translated)
```

## Demo

Run the demo script:

```bash
python demo.py
```

## Testing

- Unit tests (no API key needed):
  ```bash
  pytest tests/unit
  ```
- Integration tests (requires `DEEPL_API_KEY`):
  ```bash
  pytest tests/integration
  ```

## Design

- Follows SOLID, DRY, and KISS principles.
- High cohesion and loose coupling: Core client logic is encapsulated in `DeepLClient`.
- Secure: Reads API key from environment; handles errors gracefully.
- Well-documented: Inline docstrings and clear README.