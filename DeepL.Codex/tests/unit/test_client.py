import pytest

from deepl_translator.client import DeepLClient
from deepl_translator.exceptions import MissingAPIKeyException, DeepLException


def test_init_without_api_key(monkeypatch):
    monkeypatch.delenv("DEEPL_API_KEY", raising=False)
    with pytest.raises(MissingAPIKeyException):
        DeepLClient()


def test_translate_success(monkeypatch, requests_mock):
    api_key = "test-api-key"
    monkeypatch.setenv("DEEPL_API_KEY", api_key)
    client = DeepLClient()
    url = f"{client.DEFAULT_BASE_URL}/translate"
    sample_text = "Hello"
    target_lang = "DE"
    mock_response = {
        "translations": [
            {"detected_source_language": "EN", "text": "Hallo"}
        ]
    }
    requests_mock.post(url, json=mock_response, status_code=200)

    result = client.translate(sample_text, target_lang)
    assert result == "Hallo"


def test_translate_api_error(monkeypatch, requests_mock):
    api_key = "test-api-key"
    monkeypatch.setenv("DEEPL_API_KEY", api_key)
    client = DeepLClient()
    url = f"{client.DEFAULT_BASE_URL}/translate"
    error_message = "Invalid auth_key"
    requests_mock.post(url, json={"message": error_message}, status_code=403)

    with pytest.raises(DeepLException) as exc:
        client.translate("text", "FR")
    assert error_message in str(exc.value)


def test_translate_invalid_json(monkeypatch, requests_mock):
    api_key = "test-api-key"
    monkeypatch.setenv("DEEPL_API_KEY", api_key)
    client = DeepLClient()
    url = f"{client.DEFAULT_BASE_URL}/translate"
    requests_mock.post(url, text="Not a JSON", status_code=200)

    with pytest.raises(DeepLException):
        client.translate("text", "FR")