"""
Models for language information returned by the DeepL API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Language(BaseModel):
    """Model for a language supported by DeepL."""
    
    language: str = Field(..., description="Language code (e.g., 'EN', 'DE')")
    name: str = Field(..., description="Name of the language in English (e.g., 'English', 'German')")
    supports_formality: Optional[bool] = Field(False, description="Whether the language supports formality levels")


class SupportedLanguages(BaseModel):
    """Model for all supported languages."""
    
    source: List[Language] = Field([], description="Languages that can be translated from")
    target: List[Language] = Field([], description="Languages that can be translated to")