from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
import logging

from src.services.recommender import MovieRecommender
from src.schemas.movie import MovieRecommendation
from src.api.v1.dependencies import get_recommender_service

# Logger
logger = logging.getLogger(__name__)

# APIRouter
router = APIRouter()

@router.get(
    "/by-title", 
    response_model=List[MovieRecommendation],
    summary="Recommend movies by movie title",
    description="Finds movies similar to a given movie title based on pre-computed embeddings."
)
def recommend_by_title(
    title: str = Query(..., description="The movie title to find similar movies for."),
    n_recommendations: int = Query(10, ge=1, le=50, description="Number of recommendations to return."),
    recommender: MovieRecommender = Depends(get_recommender_service)
):
    """Endpoint to get recommendations based on a movie title."""
    logger.info(f"Received recommendation request by title: '{title}'")
    recommendations = recommender.recommend_by_movie_title(title=title, n_recommendations=n_recommendations)
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail=f"Movie with title '{title}' not found or no recommendations available."
        )
    return recommendations
