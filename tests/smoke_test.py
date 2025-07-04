import httpx
import sys

# --- Configuration ---
# The base URL of the deployed API on Render
BASE_URL = "https://movie-serving-api-main-1e80.onrender.com"
# A movie title we expect to exist in the database
TEST_MOVIE_TITLE = "Inception"
# A text query for semantic search
TEST_TEXT_QUERY = "A psychological thriller about dreams"


def run_test(test_function):
    """Decorator to run a test and print its result."""
    test_name = test_function.__name__
    print(f"[*] Running test: {test_name}...")
    try:
        test_function()
        print(f"[✔] PASSED: {test_name}\n")
        return True
    except Exception as e:
        print(f"[✖] FAILED: {test_name}")
        print(f"    Reason: {e}\n")
        return False

@run_test
def test_health_check():
    """Tests if the root endpoint is accessible and returns the correct message."""
    response = httpx.get(f"{BASE_URL}/", timeout=30)
    response.raise_for_status()  # Raises an exception for 4xx or 5xx status codes
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "ok"

@run_test
def test_recommend_by_title():
    """Tests the /by-title endpoint with a valid movie title."""
    params = {"title": TEST_MOVIE_TITLE}
    response = httpx.get(f"{BASE_URL}/api/v1/recommendations/by-title", params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0  # We expect at least one recommendation
    assert "id" in data[0] and "title" in data[0] and "similarity" in data[0]

def main():
    print("--- Starting Smoke Test for Live Movie Recommendation API ---\n")
    results = [
        test_health_check,
        test_recommend_by_title,
    ]
    
    # The tests are already run by the decorator, we just check the results
    if all(results):
        print("--- All smoke tests passed! The deployment is looking good. ---")
        sys.exit(0)
    else:
        print("--- Some smoke tests failed. Please check the logs above. ---")
        sys.exit(1)

if __name__ == "__main__":
    main()
