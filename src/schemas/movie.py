from pydantic import BaseModel, ConfigDict
from typing import Optional

class MovieRecommendation(BaseModel):
    """
    Pydantic schema for a single movie recommendation item.
    """
    id: int
    title: str
    similarity: float
    poster_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
