"""
Logging configuration for the API.
"""
import os
import logging
import json
import requests
from typing import Dict, Any, Optional

class LokiHandler(logging.Handler):
    """
    Custom logging handler that sends logs to Grafana Loki.
    """
    def __init__(self, url: str, auth: tuple, labels: Optional[Dict[str, str]] = None):
        super().__init__()
        self.url = url
        self.auth = auth
        self.labels = labels or {"app": "movie-api"}
        self.session = requests.Session()
        
    def emit(self, record: logging.LogRecord):
        try:
            log_entry = self.format(record)
            
            # Create Loki payload
            payload = {
                "streams": [
                    {
                        "stream": self.labels,
                        "values": [
                            [str(int(record.created * 1e9)), log_entry]
                        ]
                    }
                ]
            }
            
            # Send to Loki
            headers = {"Content-Type": "application/json"}
            self.session.post(
                self.url,
                auth=self.auth,
                headers=headers,
                data=json.dumps(payload),
                timeout=5
            )
        except Exception:
            # Don't raise exceptions from the logging handler
            # In a real app, you might want to handle this differently
            pass

def setup_logging():
    """Configure logging to send logs to Grafana Loki if configured."""
    loki_url = os.getenv("LOKI_URL")
    loki_username = os.getenv("LOKI_USERNAME")
    loki_password = os.getenv("LOKI_PASSWORD")
    
    # Only setup Loki if all environment variables are set
    if not (loki_url and loki_username and loki_password):
        logging.info("Loki logging not configured. Skipping.")
        return

    try:
        # Create handler
        handler = LokiHandler(
            url=loki_url,
            auth=(loki_username, loki_password),
            labels={
                "app": "movie-api",
                "environment": os.getenv("ENVIRONMENT", "production"),
                "service": "recommendation-api"
            }
        )
        
        # Set formatter for a structured log message
        formatter = logging.Formatter(
            '{"level": "%(levelname)s", "timestamp": "%(asctime)s", "logger": "%(name)s", "message": "%(message)s"}'
        )
        handler.setFormatter(formatter)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO) # Ensure root logger captures INFO level logs
        
        # Prevent duplicate logs from default handlers if any
        for h in root_logger.handlers:
            if isinstance(h, logging.StreamHandler) and h is not handler:
                root_logger.removeHandler(h)

        logging.info("Loki logging configured successfully")
    except Exception as e:
        logging.error(f"Failed to configure Loki logging: {e}") 