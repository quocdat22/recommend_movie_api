"""
Monitoring configuration using OpenTelemetry for Grafana Cloud Remote Write.
"""
import os
import logging
from fastapi import FastAPI

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus_remote_write import PrometheusRemoteWriteMetricsExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

logger = logging.getLogger(__name__)

def setup_monitoring(app: FastAPI):
    """
    Sets up OpenTelemetry monitoring, pushing metrics to Grafana Cloud.
    """
    metrics_endpoint = os.getenv("METRICS_ENDPOINT")
    metrics_username = os.getenv("METRICS_USERNAME")
    metrics_password = os.getenv("METRICS_PASSWORD")

    if not all([metrics_endpoint, metrics_username, metrics_password]):
        logger.info("OpenTelemetry Remote Write exporter is not configured. Skipping.")
        return

    try:
        # Create a Prometheus Remote Write Exporter
        exporter = PrometheusRemoteWriteMetricsExporter(
            endpoint=metrics_endpoint,
            basic_auth={'username': metrics_username, 'password': metrics_password},
        )

        # Create a metric reader to export metrics periodically
        reader = PeriodicExportingMetricReader(exporter, export_interval_millis=15000)

        # Create a MeterProvider with the reader
        meter_provider = MeterProvider(metric_readers=[reader])

        # Set the global MeterProvider
        metrics.set_meter_provider(meter_provider)

        logger.info("OpenTelemetry configured successfully for Grafana Cloud.")

        # Instrument FastAPI application to automatically capture metrics
        FastAPIInstrumentor.instrument_app(app, meter_provider=meter_provider)
        
        # Instrument the `requests` library to capture metrics from outgoing calls (e.g., to Supabase)
        RequestsInstrumentor().instrument()

    except Exception as e:
        logger.error(f"Failed to configure OpenTelemetry: {e}", exc_info=True) 