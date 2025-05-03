"""
Unit tests for the DeepL API exceptions.
"""
import unittest

from deepl.exceptions.api_exceptions import (
    DeepLAPIError,
    AuthorizationError,
    QuotaExceededError,
    RequestError,
    ConnectionError,
    ValidationError,
    handle_api_error
)


class TestAPIExceptions(unittest.TestCase):
    """Test cases for API exceptions."""

    def test_base_exception(self):
        """Test DeepLAPIError base exception."""
        # Basic exception
        error = DeepLAPIError("Test error")
        self.assertEqual(str(error), "Test error")
        self.assertIsNone(error.status_code)
        self.assertIsNone(error.response)
        
        # With status code
        error = DeepLAPIError("Test error", status_code=400)
        self.assertEqual(error.status_code, 400)
        
        # With response
        response = {"message": "Error message"}
        error = DeepLAPIError("Test error", status_code=400, response=response)
        self.assertEqual(error.response, response)
        
    def test_authorization_error(self):
        """Test AuthorizationError exception."""
        error = AuthorizationError("Invalid API key", status_code=403)
        self.assertEqual(str(error), "Invalid API key")
        self.assertEqual(error.status_code, 403)
        self.assertIsInstance(error, DeepLAPIError)
        
    def test_quota_exceeded_error(self):
        """Test QuotaExceededError exception."""
        error = QuotaExceededError("Quota exceeded", status_code=456)
        self.assertEqual(str(error), "Quota exceeded")
        self.assertEqual(error.status_code, 456)
        self.assertIsInstance(error, DeepLAPIError)
        
    def test_request_error(self):
        """Test RequestError exception."""
        error = RequestError("Bad request", status_code=400)
        self.assertEqual(str(error), "Bad request")
        self.assertEqual(error.status_code, 400)
        self.assertIsInstance(error, DeepLAPIError)
        
    def test_connection_error(self):
        """Test ConnectionError exception."""
        error = ConnectionError("Connection failed")
        self.assertEqual(str(error), "Connection failed")
        self.assertIsInstance(error, DeepLAPIError)
        
    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Invalid parameters")
        self.assertEqual(str(error), "Invalid parameters")
        self.assertIsInstance(error, DeepLAPIError)
        
    def test_handle_api_error_401(self):
        """Test handle_api_error with 401 status code."""
        response = {"message": "Unauthorized"}
        error = handle_api_error(401, response)
        self.assertIsInstance(error, AuthorizationError)
        self.assertEqual(error.status_code, 401)
        self.assertIn("Authentication error", str(error))
        
    def test_handle_api_error_403(self):
        """Test handle_api_error with 403 status code."""
        response = {"message": "Forbidden"}
        error = handle_api_error(403, response)
        self.assertIsInstance(error, AuthorizationError)
        self.assertEqual(error.status_code, 403)
        
    def test_handle_api_error_429(self):
        """Test handle_api_error with 429 status code."""
        response = {"message": "Too many requests"}
        error = handle_api_error(429, response)
        self.assertIsInstance(error, QuotaExceededError)
        self.assertEqual(error.status_code, 429)
        self.assertIn("Quota exceeded", str(error))
        
    def test_handle_api_error_456(self):
        """Test handle_api_error with 456 status code."""
        response = {"message": "Quota exceeded"}
        error = handle_api_error(456, response)
        self.assertIsInstance(error, QuotaExceededError)
        self.assertEqual(error.status_code, 456)
        
    def test_handle_api_error_400(self):
        """Test handle_api_error with 400 status code."""
        response = {"message": "Bad request"}
        error = handle_api_error(400, response)
        self.assertIsInstance(error, ValidationError)
        self.assertEqual(error.status_code, 400)
        self.assertIn("Validation error", str(error))
        
    def test_handle_api_error_other(self):
        """Test handle_api_error with other status codes."""
        response = {"message": "Server error"}
        error = handle_api_error(500, response)
        self.assertIsInstance(error, RequestError)
        self.assertEqual(error.status_code, 500)
        self.assertIn("API request error", str(error))


if __name__ == "__main__":
    unittest.main()