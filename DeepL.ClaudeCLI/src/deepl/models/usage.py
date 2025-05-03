"""
Models for usage information returned by the DeepL API.
"""
from typing import Optional
from pydantic import BaseModel, Field


class Usage(BaseModel):
    """Model for API usage information."""
    
    character_count: int = Field(..., description="Characters translated in the current billing period")
    character_limit: Optional[int] = Field(None, description="Maximum characters for the current billing period (None for unlimited)")
    
    @property
    def character_percentage(self) -> Optional[float]:
        """Calculate the percentage of the character limit used."""
        if self.character_limit is None or self.character_limit == 0:
            return None
        return (self.character_count / self.character_limit) * 100