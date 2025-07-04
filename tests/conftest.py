import sys
import os
from pathlib import Path
import pytest
from httpx import AsyncClient

# Add project root to the Python path
# This is necessary for pytest to find the 'src' module
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.main import app

@pytest.fixture(scope="session")
def anyio_backend():
    """
    Specifies the backend for anyio, required for async testing with httpx.
    """
    return "asyncio"

@pytest.fixture(scope="module")
async def async_client():
    """
    Provides an async test client for making requests to the FastAPI app.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client 