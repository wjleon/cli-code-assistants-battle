"""
Models for translation requests and responses.
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator


class TranslationRequest(BaseModel):
    """Model for translation request parameters."""
    
    text: Union[str, List[str]] = Field(..., description="Text to be translated. Multiple texts can be provided as a list.")
    target_lang: str = Field(..., description="The language to translate to")
    source_lang: Optional[str] = Field(None, description="The language to translate from. If not provided, DeepL will auto-detect the source language.")
    formality: Optional[str] = Field(None, description="Desired formality for the translation (default, more, less, prefer_more, prefer_less)")
    preserve_formatting: Optional[bool] = Field(None, description="Whether to preserve formatting")
    tag_handling: Optional[str] = Field(None, description="Type of tags to handle (xml, html)")
    split_sentences: Optional[Union[str, bool]] = Field(None, description="How to split sentences (none, '0', '1', 'nonewlines', all)")
    
    @validator('text')
    def validate_text(cls, v):
        """Validate that text is non-empty."""
        if isinstance(v, str) and not v.strip():
            raise ValueError("Text cannot be empty")
        if isinstance(v, list) and (not v or all(not t.strip() for t in v if isinstance(t, str))):
            raise ValueError("Text list cannot be empty or contain only empty strings")
        return v
    
    @validator('target_lang', 'source_lang')
    def validate_lang(cls, v):
        """Validate language codes."""
        if v is not None:
            return v.upper()
        return v
    
    def to_api_request(self) -> Dict[str, Any]:
        """Convert to the format expected by the DeepL API."""
        result = self.dict(exclude_none=True)
        
        # Ensure text is always an array
        if isinstance(result['text'], str):
            result['text'] = [result['text']]
            
        return result


class Translation(BaseModel):
    """Model for a single translation result."""
    
    detected_source_language: str = Field(..., description="Source language detected by DeepL")
    text: str = Field(..., description="Translated text")


class TranslationResponse(BaseModel):
    """Model for translation API response."""
    
    translations: List[Translation] = Field(..., description="List of translation results")