"""
DeepL API Integration package.
"""

from src.client import DeepLClient
from src.models import (
    SourceLanguage,
    TargetLanguage,
    Formality,
    SplitSentences,
    PreserveFormatting,
    TagHandling,
    OutlineDetection,
    GlossaryFormat,
    TextTranslationRequest,
    TextTranslationResponse,
    TranslatedText,
    LanguageInfo,
    SupportedLanguagesResponse,
    UsageInfo,
    GlossaryInfo,
    GlossaryListResponse,
    GlossaryCreateRequest,
    DocumentTranslationRequest,
    DocumentTranslationResponse,
    DocumentTranslationStatusResponse,
    DocumentTranslationResult,
)
from src.exceptions import (
    DeepLError,
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
    InvalidRequestError,
    UnsupportedLanguageError,
    TextTooLargeError,
    DocumentTooLargeError,
    TooManyRequestsError,
    ServerError,
    ConnectionError,
    TimeoutError,
    ResourceNotFoundError,
    GlossaryError,
    GlossaryNotFoundError,
    GlossaryLimitExceededError,
    DocumentTranslationError,
    DocumentUploadError,
    DocumentDownloadError,
    DocumentTranslationTimeoutError,
)

__all__ = [
    # Client
    "DeepLClient",
    
    # Models - Enums
    "SourceLanguage",
    "TargetLanguage",
    "Formality",
    "SplitSentences",
    "PreserveFormatting",
    "TagHandling",
    "OutlineDetection",
    "GlossaryFormat",
    
    # Models - Request/Response
    "TextTranslationRequest",
    "TextTranslationResponse",
    "TranslatedText",
    "LanguageInfo",
    "SupportedLanguagesResponse",
    "UsageInfo",
    "GlossaryInfo",
    "GlossaryListResponse",
    "GlossaryCreateRequest",
    "DocumentTranslationRequest",
    "DocumentTranslationResponse",
    "DocumentTranslationStatusResponse",
    "DocumentTranslationResult",
    
    # Exceptions
    "DeepLError",
    "AuthenticationError",
    "QuotaExceededError",
    "RateLimitError",
    "InvalidRequestError",
    "UnsupportedLanguageError",
    "TextTooLargeError",
    "DocumentTooLargeError",
    "TooManyRequestsError",
    "ServerError",
    "ConnectionError",
    "TimeoutError",
    "ResourceNotFoundError",
    "GlossaryError",
    "GlossaryNotFoundError",
    "GlossaryLimitExceededError",
    "DocumentTranslationError",
    "DocumentUploadError",
    "DocumentDownloadError",
    "DocumentTranslationTimeoutError",
]

# Version information
__version__ = "0.1.0"
