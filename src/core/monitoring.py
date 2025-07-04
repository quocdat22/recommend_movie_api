"""
Monitoring configuration for the API, specifically for Grafana Cloud Remote Write.
"""
import os
import logging
import threading
import time
from typing import Callable

import requests
import snappy
from fastapi import FastAPI
from prometheus_client import REGISTRY, exposition

logger = logging.getLogger(__name__)


class GrafanaCloudRemoteWriteExporter:
    """
    Exports metrics to Grafana Cloud using the Prometheus Remote Write protocol.
    This implementation is more robust for Grafana Cloud than using push_to_gateway.
    """

    def __init__(self, app_name: str = "movie-api"):
        self.app_name = app_name
        self.remote_write_url = os.getenv("METRICS_ENDPOINT")
        self.username = os.getenv("METRICS_USERNAME")
        self.password = os.getenv("METRICS_PASSWORD")
        self.push_interval = int(os.getenv("METRICS_PUSH_INTERVAL", "15"))
        self.registry = REGISTRY

        self.is_enabled = all([self.remote_write_url, self.username, self.password])
        self._stop_event = threading.Event()
        self._thread = None
        self.session = requests.Session()
        
        if self.is_enabled:
            # The assert calls are for the type checker to understand that these are not None.
            assert self.username is not None
            assert self.password is not None
            self.session.auth = (self.username, self.password)
        
        self.session.headers.update({
            "Content-Type": "application/x-protobuf",
            "Content-Encoding": "snappy",
            "X-Prometheus-Remote-Write-Version": "0.1.0"
        })

    def start(self):
        if not self.is_enabled:
            logger.info("Grafana Cloud Remote Write exporter is not configured. Skipping.")
            return

        logger.info(f"Starting Remote Write exporter to {self.remote_write_url} every {self.push_interval}s")
        self._thread = threading.Thread(target=self._push_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if self._thread:
            self._stop_event.set()
            self._thread.join(timeout=5)
            logger.info("Remote Write exporter stopped.")

    def _push_loop(self):
        while not self._stop_event.is_set():
            try:
                self._push_metrics()
            except Exception as e:
                logger.error(f"Failed to push metrics to Grafana Cloud: {e}", exc_info=True)
            self._stop_event.wait(self.push_interval)

    def _push_metrics(self):
        # Generate metrics in Prometheus protobuf format
        proto_data = exposition.generate_latest(self.registry, 'application/vnd.google.protobuf; proto=io.prometheus.client.MetricFamily; encoding=delimited')
        
        # Compress with snappy
        compressed_data = snappy.compress(proto_data)

        try:
            if not self.remote_write_url:
                logger.error("Remote write URL is not set, cannot push metrics.")
                return

            response = self.session.post(self.remote_write_url, data=compressed_data, timeout=10)
            response.raise_for_status()  # This will raise an exception for 4xx/5xx errors
            logger.debug(f"Successfully pushed metrics to Grafana Cloud. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending metrics to Grafana Cloud: {e}")
            # Optionally log response body for more details if available
            if e.response is not None:
                logger.error(f"Response body: {e.response.text}")


def setup_monitoring(app: FastAPI):
    """Set up monitoring for the FastAPI application."""
    exporter = GrafanaCloudRemoteWriteExporter()

    @app.on_event("startup")
    def startup_metrics():
        exporter.start()

    @app.on_event("shutdown")
    def shutdown_metrics():
        exporter.stop()

    return exporter 