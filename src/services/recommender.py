"""
This module contains the movie recommendation service, which is responsible
for loading the necessary models and providing movie recommendations.
"""

import logging
from typing import Optional, List, Dict
import pandas as pd
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

from src.core.config import get_settings, Settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MovieRecommender:
    """Movie recommendation system using Supabase pgvector and Sentence Transformers."""

    def __init__(self, settings: Settings):
        """
        Initialize the movie recommender with application settings.
        
        Args:
            settings: The application settings object.
        """
        self.settings = settings
        self.supabase: Client = self._init_supabase_client()
        self.transformer_model: Optional[SentenceTransformer] = self._load_transformer_model()

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

    def _load_transformer_model(self) -> Optional[SentenceTransformer]:
        """Loads and returns the Sentence Transformer model from settings."""
        try:
            model_name = self.settings.yaml_config['models']['transformer']['name']
        except KeyError:
            logger.error("Transformer model name not found in YAML config.")
            return None

        try:
            logger.info(f"Loading Sentence Transformer model: {model_name}")
            model = SentenceTransformer(model_name)
            logger.info("Sentence Transformer model loaded successfully.")
            return model
        except Exception as e:
            logger.error(f"Failed to load Sentence Transformer model: {e}")
            return None

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

    def recommend_by_text(
        self, 
        query: str, 
        n_recommendations: int = 10,
        match_threshold: float = 0.45
    ) -> List[Dict]:
        """
        Recommend movies based on a text query.
        Returns a list of dictionaries instead of a DataFrame.
        """
        if not self.transformer_model:
            logger.error("Sentence Transformer model is not available.")
            return []

        logger.info(f"Generating embedding for query: '{query}'")
        query_embedding = self.transformer_model.encode(query)
        embedding_list = query_embedding.tolist()

        logger.info("Fetching recommendations based on text query...")
        try:
            rpc_params = {
                'query_embedding': embedding_list,
                'match_count': n_recommendations,
                'match_threshold': match_threshold
            }
            recommendations_response = self.supabase.rpc("match_movies_by_text_embedding", rpc_params).execute()
            
            recs_data = recommendations_response.data
            if not recs_data:
                logger.warning("No similar movies found for the query.")
                return []

            logger.info(f"Found {len(recs_data)} recommendations.")
            return recs_data
        except Exception as e:
            logger.error(f"An error occurred while fetching text-based recommendations: {e}")
            return []
