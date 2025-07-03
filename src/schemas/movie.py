from pydantic import BaseModel, ConfigDict
from typing import Optional

class MovieRecommendation(BaseModel):
    """
    Pydantic schema for a single movie recommendation item.
    """
    id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    similarity: float

    model_config = ConfigDict(from_attributes=True)
