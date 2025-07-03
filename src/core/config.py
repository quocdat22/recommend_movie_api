import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Dict, Any, Optional
import os

def get_config_path():
    return os.environ.get("CONFIG_PATH", "configs/settings.yaml")

@lru_cache
def load_yaml_config(path: str) -> Dict[str, Any]:
    """Load YAML config file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)

class Settings(BaseSettings):
    """
    Pydantic settings class to manage application configuration.
    Reads environment variables and YAML config.
    """
    # Environment variables
    SUPABASE_URL: str
    SUPABASE_KEY: str
    CONFIG_PATH: Optional[str] = None

    # YAML configuration
    @property
    def yaml_config(self) -> Dict[str, Any]:
        return load_yaml_config(get_config_path())

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Get the application settings.
    The lru_cache decorator ensures this function is only called once.
    """
    return Settings()
