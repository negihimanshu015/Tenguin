import json
import logging
import datetime
from .context import get_correlation_id

class CorrelationIdFilter(logging.Filter):
    """
    Log filter to inject the current request's correlation ID into the log record.
    """
    def filter(self, record):
        record.correlation_id = get_correlation_id()
        return True

class JSONFormatter(logging.Formatter):
    """
    Formatter to output logs in JSON format.
    """
    def format(self, record):
        log_data = {
            "timestamp": datetime.datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "path": record.pathname,
            "line_number": record.lineno,
            "correlation_id": getattr(record, "correlation_id", None),
        }
        
        # safely add extra fields that might have been passed
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "duration"):
            log_data["duration"] = record.duration
            
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)
