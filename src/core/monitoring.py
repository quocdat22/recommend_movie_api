"""
Monitoring configuration for the API.
"""
import os
import logging
import time
from typing import Callable
from fastapi import FastAPI
from prometheus_client import push_to_gateway, REGISTRY
import threading

logger = logging.getLogger(__name__)

class GrafanaCloudMetricsExporter:
    """
    Export metrics to Grafana Cloud using Prometheus remote write.
    """
    def __init__(self, app_name: str = "movie-api"):
        self.app_name = app_name
        self.metrics_endpoint = os.getenv("METRICS_ENDPOINT")
        self.metrics_username = os.getenv("METRICS_USERNAME")
        self.metrics_password = os.getenv("METRICS_PASSWORD")
        self.registry = REGISTRY
        self.push_interval = int(os.getenv("METRICS_PUSH_INTERVAL", "15"))  # seconds
        self.is_enabled = bool(self.metrics_endpoint and self.metrics_username and self.metrics_password)
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        """Start the metrics push thread if configuration is available."""
        if not self.is_enabled:
            logger.info("Grafana Cloud metrics export not configured. Skipping.")
            return
        
        logger.info(f"Starting metrics push to {self.metrics_endpoint} every {self.push_interval}s")
        self._thread = threading.Thread(target=self._push_metrics_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the metrics push thread."""
        if self._thread:
            self._stop_event.set()
            self._thread.join(timeout=5)
            logger.info("Metrics push thread stopped")

    def _push_metrics_loop(self):
        """Push metrics to Grafana Cloud at regular intervals."""
        while not self._stop_event.is_set():
            try:
                self._push_metrics()
            except Exception as e:
                logger.error(f"Error pushing metrics to Grafana Cloud: {e}")
            
            # Sleep until next interval or stop event
            self._stop_event.wait(self.push_interval)

    def _push_metrics(self):
        """Push current metrics to Grafana Cloud."""
        if not self.is_enabled:
            return
        
        try:
            # Use basic auth for Grafana Cloud
            push_to_gateway(
                gateway=self.metrics_endpoint,
                job=self.app_name,
                registry=self.registry,
                handler=self._basic_auth_handler()
            )
            logger.debug("Successfully pushed metrics to Grafana Cloud")
        except Exception as e:
            logger.error(f"Failed to push metrics: {e}")

    def _basic_auth_handler(self) -> Callable:
        """Create a basic auth handler for the Prometheus push gateway."""
        import base64
        import urllib.request
        
        auth = f"{self.metrics_username}:{self.metrics_password}"
        encoded_auth = base64.b64encode(auth.encode()).decode()
        
        def handler(url, method, timeout, headers, data):
            request = urllib.request.Request(url=url, data=data, headers=headers, method=method)
            request.add_header("Authorization", f"Basic {encoded_auth}")
            return urllib.request.urlopen(request, timeout=timeout)
        
        return handler

def setup_monitoring(app: FastAPI):
    """Set up monitoring for the FastAPI application."""
    # Create and start the metrics exporter
    metrics_exporter = GrafanaCloudMetricsExporter()
    
    @app.on_event("startup")
    def startup_metrics():
        metrics_exporter.start()
    
    # Add event handlers to manage the exporter lifecycle
    @app.on_event("shutdown")
    def shutdown_metrics():
        metrics_exporter.stop()
    
    # Return the exporter in case it's needed elsewhere
    return metrics_exporter 