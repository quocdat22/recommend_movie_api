from functools import lru_cache
from src.services.recommender import MovieRecommender
from src.core.config import get_settings

@lru_cache()
def get_recommender_service() -> MovieRecommender:
    """
    Dependency injection function for the MovieRecommender service.
    Using lru_cache ensures that the service is initialized only once.
    """
    settings = get_settings()
    return MovieRecommender(settings) 