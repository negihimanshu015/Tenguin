import contextvars
import uuid

_correlation_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=None
)


def get_correlation_id() -> str:
    """Get the correlation ID for the current request."""
    return _correlation_id_ctx_var.get()


def set_correlation_id(correlation_id: str) -> contextvars.Token:
    """Set the correlation ID for the current request."""
    return _correlation_id_ctx_var.set(correlation_id)


def reset_correlation_id(token: contextvars.Token) -> None:
    """Reset the correlation ID context variable."""
    _correlation_id_ctx_var.reset(token)


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())
