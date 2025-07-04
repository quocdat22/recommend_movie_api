from fastapi import FastAPI
from src.api.v1 import recommend as recommend_v1
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import request_size, response_size, latency, requests

# Import the new setup functions
from src.core.logging import setup_logging
from src.core.monitoring import setup_monitoring

# Configure logging to send logs to Grafana Loki if configured
setup_logging()

# Configure standard logging
# logging.basicConfig(level=logging.INFO) # This is now handled by setup_logging
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title="Movie Recommendation API",
    description="API for serving movie recommendations based on different models.",
    version="1.0.0"
)

# Configure the instrumentator with enhanced metrics
instrumentator = Instrumentator(
    should_instrument_requests=True,
    should_instrument_responses=True,
    excluded_handlers=["/metrics"],
)
instrumentator.add(requests(metric_name="http_requests_total", metric_doc="Total number of requests by method, status and handler."))
instrumentator.add(latency(metric_name="http_request_duration_seconds", metric_doc="Latency of requests in seconds."))
instrumentator.add(request_size(metric_name="http_request_size_bytes", metric_doc="Size of requests in bytes."))
instrumentator.add(response_size(metric_name="http_response_size_bytes", metric_doc="Size of responses in bytes."))

# Instrument the app. Note: .expose() is not called as we push metrics.
instrumentator.instrument(app)

# Setup monitoring to push metrics to Grafana Cloud
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
