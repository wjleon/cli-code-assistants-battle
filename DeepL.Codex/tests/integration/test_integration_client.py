import os
import pytest

from deepl_translator.client import DeepLClient
from deepl_translator.exceptions import DeepLException

# Skip integration tests if API key is not set
if not os.getenv("DEEPL_API_KEY"):
    pytest.skip(
        "DEEPL_API_KEY environment variable not set. Skipping integration tests.",
        allow_module_level=True,
    )

@pytest.fixture(scope="module")
def client():
    return DeepLClient()

@pytest.mark.parametrize(
    "text,target",
    [
        ("Hola", "EN"),
        ("Hello", "UK"),
        ("Buongiorno", "IT"),
    ],
)
def test_integration_translate(client, text, target):
    result = client.translate(text, target)
    assert isinstance(result, str)
    assert result.strip() != ""