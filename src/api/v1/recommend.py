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

@router.get(
    "/by-text", 
    response_model=List[MovieRecommendation],
    summary="Recommend movies by a text query",
    description="Generates embeddings for the text query and finds movies with similar semantic content."
)
def recommend_by_text(
    query: str = Query(..., min_length=3, description="The text query to find relevant movies for."),
    n_recommendations: int = Query(10, ge=1, le=50, description="Number of recommendations to return."),
    recommender: MovieRecommender = Depends(get_recommender_service)
):
    """Endpoint to get recommendations based on a text query."""
    logger.info(f"Received recommendation request by text: '{query}'")
    if not recommender.transformer_model:
        raise HTTPException(
            status_code=503,
            detail="The text-based recommendation service is currently unavailable."
        )
    recommendations = recommender.recommend_by_text(query=query, n_recommendations=n_recommendations)
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail=f"No movies found matching the query: '{query}'."
        )
    return recommendations
