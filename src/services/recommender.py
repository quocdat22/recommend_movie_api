"""
This module contains the movie recommendation service, which is responsible
for loading the necessary models and providing movie recommendations.
"""

import logging
from typing import Optional, List, Dict
import pandas as pd
from supabase import create_client, Client

from src.core.config import Settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MovieRecommender:
    """Movie recommendation system using Supabase pgvector."""

    def __init__(self, settings: Settings):
        """
        Initialize the movie recommender with application settings.
        
        Args:
            settings: The application settings object.
        """
        self.settings = settings
        self.supabase: Client = self._init_supabase_client()

    def _init_supabase_client(self) -> Client:
        """Initializes and returns the Supabase client using settings."""
        logger.info("Initializing Supabase client...")
        url = self.settings.SUPABASE_URL
        key = self.settings.SUPABASE_KEY
        if not url or not key:
            logger.error("Supabase credentials not found in settings.")
            raise ValueError("Supabase URL and Key must be set.")
        logger.info("Supabase client initialized successfully.")
        return create_client(url, key)

    def recommend_by_movie_title(
        self, 
        title: str, 
        n_recommendations: int = 10, 
        match_threshold: float = 0.4
    ) -> List[Dict]:
        """
        Recommend movies similar to a given movie title.
        Returns a list of dictionaries instead of a DataFrame.
        """
        logger.info(f"Finding movie ID for title: '{title}'")
        try:
            movie_response = self.supabase.table("movies").select("id").eq("title", title).limit(1).single().execute()
            movie_id = movie_response.data['id']
            logger.info(f"Found movie ID: {movie_id}")
        except Exception as e:
            logger.error(f"Could not find movie with title '{title}'. Error: {e}")
            return []

        logger.info(f"Fetching recommendations for movie ID {movie_id}...")
        try:
            rpc_params = {
                'p_movie_id': movie_id,
                'match_count': n_recommendations,
                'match_threshold': match_threshold
            }
            recommendations_response = self.supabase.rpc("match_movies", rpc_params).execute()
            
            recs_data = recommendations_response.data
            if not recs_data:
                logger.warning("No similar movies found above the threshold.")
                return []
                
            logger.info(f"Found {len(recs_data)} recommendations.")
            return recs_data
        except Exception as e:
            logger.error(f"An error occurred while fetching recommendations: {e}")
            return []
