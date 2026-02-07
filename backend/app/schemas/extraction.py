from pydantic import BaseModel
from typing import List, Optional


class ExtractedEntity(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = "Entity"
    confidence: Optional[float] = None


class ExtractedRelationship(BaseModel):
    source: Optional[str] = None
    target: Optional[str] = None
    type: Optional[str] = "RELATED_TO"
    confidence: Optional[float] = None


class ExtractionResult(BaseModel):
    entities: List[ExtractedEntity]
    relationships: List[ExtractedRelationship]
