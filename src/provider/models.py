from typing import List, Optional
from pydantic import BaseModel, Field


class Provider(BaseModel):
    """OpenAI-compatible provider configuration"""
    name: str = Field(..., description="Unique provider name")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(..., description="API authentication key")
    models: List[str] = Field(default_factory=list, description="List of available model identifiers")

    class Config:
        frozen = False  # Allow modification for runtime updates
