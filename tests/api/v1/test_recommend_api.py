import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from src.main import app
from src.api.v1.dependencies import get_recommender_service

# Mock the recommender service
mock_recommender_service = MagicMock()

def get_mock_recommender_service_override():
    """This function will override the original dependency."""
    return mock_recommender_service

# Apply the dependency override to the app
app.dependency_overrides[get_recommender_service] = get_mock_recommender_service_override

# Create a TestClient
client = TestClient(app)

# Sample data to be returned by the mock
FAKE_MOVIE_RECS = [
    {'id': 1, 'title': 'Test Movie 1', 'overview': 'An overview', 'release_date': '2022-01-01', 'similarity': 0.9},
    {'id': 2, 'title': 'Test Movie 2', 'overview': 'Another overview', 'release_date': '2022-01-02', 'similarity': 0.8}
]

@pytest.fixture(autouse=True)
def reset_mock_before_each_test():
    """A fixture to reset the mock's state before each test function runs."""
    mock_recommender_service.reset_mock()

def test_health_check():
    """Test the root endpoint to ensure the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Welcome to the Movie Recommendation API!"}

def test_recommend_by_title_success():
    """Test the happy path for recommending movies by title."""
    # Configure the mock to return our fake data for this specific test
    mock_recommender_service.recommend_by_movie_title.return_value = FAKE_MOVIE_RECS

    # Make the API call
    response = client.get("/api/v1/recommendations/by-title?title=Inception")

    # Assert the response is correct
    assert response.status_code == 200
    assert response.json() == FAKE_MOVIE_RECS

    # Assert that our mock service was called with the correct parameters
    mock_recommender_service.recommend_by_movie_title.assert_called_once_with(title="Inception", n_recommendations=10)

def test_recommend_by_title_movie_not_found():
    """Test the case where no recommendations are found for a title."""
    # Configure the mock to return an empty list
    mock_recommender_service.recommend_by_movie_title.return_value = []

    # Make the API call
    response = client.get("/api/v1/recommendations/by-title?title=UnknownMovie")

    # Assert the API returns a 404 Not Found error
    assert response.status_code == 404
    assert "not found or no recommendations available" in response.json()["detail"]

    # Assert that our mock service was still called correctly
    mock_recommender_service.recommend_by_movie_title.assert_called_once_with(title="UnknownMovie", n_recommendations=10)

def test_recommend_by_title_missing_query_param():
    """Test the API's response when the 'title' query parameter is missing."""
    response = client.get("/api/v1/recommendations/by-title")
    # FastAPI should automatically return a 422 for validation errors
    assert response.status_code == 422
