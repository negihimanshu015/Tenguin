import logging
import time

from .context import generate_correlation_id, reset_correlation_id, set_correlation_id

logger = logging.getLogger(__name__)

class RequestCorrelationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = generate_correlation_id()

        token = set_correlation_id(correlation_id)

        response = self.get_response(request)

        response["X-Correlation-ID"] = correlation_id

        duration = (time.time() - start_time) * 1000
        logger.info(
            "Request finished %s %s %d",
            request.method,
            request.get_full_path(),
            response.status_code,
            extra={
                "status_code": response.status_code,
                "method": request.method,
                "path": request.get_full_path(),
                "duration": duration,
            }
        )

        reset_correlation_id(token)

        return response
