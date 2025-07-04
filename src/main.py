from fastapi import FastAPI
from src.api.v1 import recommend as recommend_v1
import logging

# Import the new setup functions
from src.core.logging import setup_logging
from src.core.monitoring import setup_monitoring

# Configure logging to send logs to Grafana Loki if configured
setup_logging()

logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title="Movie Recommendation API",
    description="API for serving movie recommendations based on different models.",
    version="1.0.0"
)

# Setup OpenTelemetry monitoring
# This will instrument the app and start exporting metrics.
setup_monitoring(app)

# Include routers
logger.info("Including API routers...")
app.include_router(recommend_v1.router, prefix="/api/v1/recommendations", tags=["v1"])
logger.info("Routers included successfully.")

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"status": "ok", "message": "Welcome to the Movie Recommendation API!"}
