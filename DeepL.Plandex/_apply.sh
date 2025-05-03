#!/bin/zsh

set -euo pipefail

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not found. Please install pip3 and try again."
    exit 1
fi

echo "=== Installing dependencies ==="
pip3 install -r requirements.txt || {
    echo "Error: Failed to install dependencies."
    exit 1
}

echo "=== Installing package in development mode ==="
pip3 install -e . || {
    echo "Error: Failed to install package in development mode."
    exit 1
}

echo "=== Running unit tests ==="
python3 -m pytest tests/unit/ -v || {
    echo "Error: Unit tests failed."
    exit 1
}

echo "=== Running demo script ==="
# Check if DEEPL_API_KEY is set
if [ -z "$DEEPL_API_KEY" ]; then
    echo "Warning: DEEPL_API_KEY environment variable is not set."
    echo "The demo script requires a valid DeepL API key to run."
    echo "Please set the DEEPL_API_KEY environment variable and try again."
    echo "Example: export DEEPL_API_KEY=your-api-key"
    echo ""
    echo "You can get a free API key by signing up at https://www.deepl.com/pro#developer"
    echo ""
    echo "Skipping demo script execution."
else
    python3 demo.py || {
        echo "Error: Demo script failed."
        exit 1
    }
fi

echo "=== All tasks completed successfully ==="
