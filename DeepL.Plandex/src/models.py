"""
Data models for DeepL API integration.

This module defines Pydantic models for requests and responses when interacting
with the DeepL API, providing validation and serialization/deserialization.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator


class SourceLanguage(str, Enum):
    """Supported source languages for translation."""
    AUTO = "auto"  # Auto-detect language
    BG = "BG"      # Bulgarian
    CS = "CS"      # Czech
    DA = "DA"      # Danish
    DE = "DE"      # German
    EL = "EL"      # Greek
    EN = "EN"      # English
    ES = "ES"      # Spanish
    ET = "ET"      # Estonian
    FI = "FI"      # Finnish
    FR = "FR"      # French
    HU = "HU"      # Hungarian
    ID = "ID"      # Indonesian
    IT = "IT"      # Italian
    JA = "JA"      # Japanese
    KO = "KO"      # Korean
    LT = "LT"      # Lithuanian
    LV = "LV"      # Latvian
    NB = "NB"      # Norwegian (Bokmål)
    NL = "NL"      # Dutch
    PL = "PL"      # Polish
    PT = "PT"      # Portuguese
    RO = "RO"      # Romanian
    RU = "RU"      # Russian
    SK = "SK"      # Slovak
    SL = "SL"      # Slovenian
    SV = "SV"      # Swedish
    TR = "TR"      # Turkish
    UK = "UK"      # Ukrainian
    ZH = "ZH"      # Chinese


class TargetLanguage(str, Enum):
    """Supported target languages for translation."""
    BG = "BG"      # Bulgarian
    CS = "CS"      # Czech
    DA = "DA"      # Danish
    DE = "DE"      # German
    EL = "EL"      # Greek
    EN = "EN"      # English (unspecified variant)
    EN_GB = "EN-GB"  # English (British)
    EN_US = "EN-US"  # English (American)
    ES = "ES"      # Spanish
    ET = "ET"      # Estonian
    FI = "FI"      # Finnish
    FR = "FR"      # French
    HU = "HU"      # Hungarian
    ID = "ID"      # Indonesian
    IT = "IT"      # Italian
    JA = "JA"      # Japanese
    KO = "KO"      # Korean
    LT = "LT"      # Lithuanian
    LV = "LV"      # Latvian
    NB = "NB"      # Norwegian (Bokmål)
    NL = "NL"      # Dutch
    PL = "PL"      # Polish
    PT = "PT"      # Portuguese (unspecified variant)
    PT_BR = "PT-BR"  # Portuguese (Brazilian)
    PT_PT = "PT-PT"  # Portuguese (European)
    RO = "RO"      # Romanian
    RU = "RU"      # Russian
    SK = "SK"      # Slovak
    SL = "SL"      # Slovenian
    SV = "SV"      # Swedish
    TR = "TR"      # Turkish
    UK = "UK"      # Ukrainian
    ZH = "ZH"      # Chinese (simplified)


class Formality(str, Enum):
    """Formality options for translations."""
    DEFAULT = "default"
    MORE = "more"
    LESS = "less"
    PREFER_MORE = "prefer_more"
    PREFER_LESS = "prefer_less"


class SplitSentences(str, Enum):
    """Options for how the translation engine should split sentences."""
    OFF = "0"
    ON = "1"
    NO_NEWLINES = "nonewlines"


class PreserveFormatting(str, Enum):
    """Options for preserving formatting."""
    OFF = "0"
    ON = "1"


class TagHandling(str, Enum):
    """Options for handling tags in the source text."""
    XML = "xml"
    HTML = "html"


class OutlineDetection(str, Enum):
    """Options for outline detection."""
    OFF = "0"
    ON = "1"


class GlossaryFormat(str, Enum):
    """Supported glossary formats."""
    CSV = "csv"
    TSV = "tsv"


class DocumentInputFormat(str, Enum):
    """Supported input document formats."""
    DOCX = "docx"
    PPTX = "pptx"
    PDF = "pdf"
    XLSX = "xlsx"
    HTML = "html"
    HTM = "htm"
    TXT = "txt"


class DocumentOutputFormat(str, Enum):
    """Supported output document formats."""
    DOCX = "docx"
    PPTX = "pptx"
    PDF = "pdf"
    XLSX = "xlsx"
    HTML = "html"
    TXT = "txt"
    # Output format is typically the same as input format, except for HTM which outputs as HTML


class TextTranslationRequest(BaseModel):
    """Model for text translation requests."""
    text: Union[str, List[str]] = Field(..., description="Text to be translated. This can be a string or a list of strings.")
    source_lang: Optional[SourceLanguage] = Field(SourceLanguage.AUTO, description="Language of the text to be translated. If not specified, the API will auto-detect the language.")
    target_lang: TargetLanguage = Field(..., description="Language into which the text should be translated.")
    split_sentences: Optional[SplitSentences] = Field(SplitSentences.ON, description="Controls how the translation engine should split sentences.")
    preserve_formatting: Optional[PreserveFormatting] = Field(PreserveFormatting.OFF, description="Controls whether the translation engine should preserve some aspects of the formatting.")
    formality: Optional[Formality] = Field(Formality.DEFAULT, description="Controls whether the translated text should lean towards formal or informal language.")
    glossary_id: Optional[str] = Field(None, description="ID of a glossary to use for the translation.")
    tag_handling: Optional[TagHandling] = Field(None, description="Controls how tagged content should be handled.")
    outline_detection: Optional[OutlineDetection] = Field(OutlineDetection.ON, description="Controls whether outline detection should be used.")
    non_splitting_tags: Optional[List[str]] = Field(None, description="List of XML tags that should not be used to split sentences.")
    splitting_tags: Optional[List[str]] = Field(None, description="List of XML tags that should be used to split sentences.")
    ignore_tags: Optional[List[str]] = Field(None, description="List of XML tags that should be ignored.")

    @validator('text')
    def validate_text(cls, v):
        """Validate that text is not empty."""
        if isinstance(v, str) and not v.strip():
            raise ValueError("Text cannot be empty")
        if isinstance(v, list) and (not v or all(not t.strip() for t in v if isinstance(t, str))):
            raise ValueError("Text list cannot be empty or contain only empty strings")
        return v

    def to_api_params(self) -> Dict[str, Any]:
        """Convert the model to parameters for the API request."""
        params = {}
        
        # Handle text parameter (could be a single string or a list)
        if isinstance(self.text, list):
            for i, text_item in enumerate(self.text):
                params[f'text={i}'] = text_item
        else:
            params['text'] = self.text
            
        # Add other parameters
        if self.source_lang != SourceLanguage.AUTO:
            params['source_lang'] = self.source_lang.value
            
        params['target_lang'] = self.target_lang.value
        
        if self.split_sentences != SplitSentences.ON:
            params['split_sentences'] = self.split_sentences.value
            
        if self.preserve_formatting != PreserveFormatting.OFF:
            params['preserve_formatting'] = self.preserve_formatting.value
            
        if self.formality != Formality.DEFAULT:
            params['formality'] = self.formality.value
            
        if self.glossary_id:
            params['glossary_id'] = self.glossary_id
            
        if self.tag_handling:
            params['tag_handling'] = self.tag_handling.value
            
        if self.outline_detection != OutlineDetection.ON:
            params['outline_detection'] = self.outline_detection.value
            
        if self.non_splitting_tags:
            params['non_splitting_tags'] = ','.join(self.non_splitting_tags)
            
        if self.splitting_tags:
            params['splitting_tags'] = ','.join(self.splitting_tags)
            
        if self.ignore_tags:
            params['ignore_tags'] = ','.join(self.ignore_tags)
            
        return params


class TranslatedText(BaseModel):
    """Model for a single translated text."""
    text: str = Field(..., description="Translated text.")
    detected_source_language: SourceLanguage = Field(..., description="Language detected in the source text.")


class TextTranslationResponse(BaseModel):
    """Model for text translation responses."""
    translations: List[TranslatedText] = Field(..., description="List of translated texts.")


class LanguageInfo(BaseModel):
    """Model for language information."""
    language: str = Field(..., description="Language code.")
    name: str = Field(..., description="Language name (in English).")
    supports_formality: Optional[bool] = Field(False, description="Whether the language supports formality.")


class SupportedLanguagesResponse(BaseModel):
    """Model for supported languages response."""
    source_languages: List[LanguageInfo] = Field(..., description="List of supported source languages.")
    target_languages: List[LanguageInfo] = Field(..., description="List of supported target languages.")


class UsageInfo(BaseModel):
    """Model for usage information."""
    character_count: int = Field(..., description="Number of characters translated.")
    character_limit: int = Field(..., description="Character limit for the account.")


class GlossaryEntry(BaseModel):
    """Model for a glossary entry."""
    source: str = Field(..., description="Source term.")
    target: str = Field(..., description="Target term.")


class GlossaryEntries(BaseModel):
    """Model for glossary entries."""
    entries: List[GlossaryEntry] = Field(..., description="List of glossary entries.")


class GlossaryCreateRequest(BaseModel):
    """Model for glossary creation requests."""
    name: str = Field(..., description="Name of the glossary.")
    source_lang: SourceLanguage = Field(..., description="Source language of the glossary.")
    target_lang: TargetLanguage = Field(..., description="Target language of the glossary.")
    entries: Union[str, GlossaryEntries] = Field(..., description="Glossary entries as a string in the specified format or as a structured object.")
    entries_format: Optional[GlossaryFormat] = Field(GlossaryFormat.CSV, description="Format of the entries if provided as a string.")

    @validator('name')
    def validate_name(cls, v):
        """Validate that name is not empty."""
        if not v.strip():
            raise ValueError("Glossary name cannot be empty")
        return v

    @validator('entries')
    def validate_entries(cls, v, values):
        """Validate that entries are not empty."""
        if isinstance(v, str) and not v.strip():
            raise ValueError("Glossary entries cannot be empty")
        if isinstance(v, GlossaryEntries) and not v.entries:
            raise ValueError("Glossary entries cannot be empty")
        return v


class GlossaryInfo(BaseModel):
    """Model for glossary information."""
    glossary_id: str = Field(..., description="ID of the glossary.")
    name: str = Field(..., description="Name of the glossary.")
    source_lang: SourceLanguage = Field(..., description="Source language of the glossary.")
    target_lang: TargetLanguage = Field(..., description="Target language of the glossary.")
    creation_time: str = Field(..., description="Creation time of the glossary.")
    entry_count: int = Field(..., description="Number of entries in the glossary.")


class GlossaryListResponse(BaseModel):
    """Model for glossary list response."""
    glossaries: List[GlossaryInfo] = Field(..., description="List of glossaries.")


class DocumentTranslationRequest(BaseModel):
    """Model for document translation requests."""
    source_lang: Optional[SourceLanguage] = Field(SourceLanguage.AUTO, description="Language of the document to be translated.")
    target_lang: TargetLanguage = Field(..., description="Language into which the document should be translated.")
    formality: Optional[Formality] = Field(Formality.DEFAULT, description="Controls whether the translated text should lean towards formal or informal language.")
    glossary_id: Optional[str] = Field(None, description="ID of a glossary to use for the translation.")
    # Note: The actual file is not part of this model as it will be sent as a multipart/form-data request


class DocumentTranslationResponse(BaseModel):
    """Model for document translation responses."""
    document_id: str = Field(..., description="ID of the document translation job.")
    document_key: str = Field(..., description="Key for the document translation job.")


class DocumentTranslationStatusResponse(BaseModel):
    """Model for document translation status responses."""
    document_id: str = Field(..., description="ID of the document translation job.")
    status: str = Field(..., description="Status of the document translation job.")
    seconds_remaining: Optional[int] = Field(None, description="Estimated number of seconds until the translation is done.")
    billed_characters: Optional[int] = Field(None, description="Number of characters billed for the translation.")


class DocumentTranslationResult(BaseModel):
    """Model for document translation results."""
    document_id: str = Field(..., description="ID of the document translation job.")
    document_key: str = Field(..., description="Key for the document translation job.")
    # Note: The actual file content is not part of this model as it will be received as a file download
