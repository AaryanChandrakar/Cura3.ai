"""
Cura3.ai — Azure Application Insights Integration
Provides telemetry, error tracking, and performance monitoring.

To activate, set APPINSIGHTS_CONNECTION_STRING in environment variables.
When the connection string is not set, all telemetry functions become no-ops.
"""
import logging
import os
from functools import wraps
from time import time

logger = logging.getLogger("cura3.monitoring")

# ── Connection String ────────────────────────────────────
_CONNECTION_STRING = os.getenv("APPINSIGHTS_CONNECTION_STRING", "")
_ENABLED = bool(_CONNECTION_STRING)

# ── Initialize Azure Monitor (if configured) ────────────
_tracer = None
_exporter = None

if _ENABLED:
    try:
        from opencensus.ext.azure.trace_exporter import AzureExporter
        from opencensus.trace.tracer import Tracer
        from opencensus.trace.samplers import ProbabilitySampler

        _exporter = AzureExporter(connection_string=_CONNECTION_STRING)
        _tracer = Tracer(
            exporter=_exporter,
            sampler=ProbabilitySampler(rate=1.0),  # Sample 100% of requests
        )
        logger.info("[MONITORING] Azure Application Insights enabled.")
    except ImportError:
        logger.warning(
            "[MONITORING] opencensus-ext-azure not installed. "
            "Run: pip install opencensus-ext-azure"
        )
        _ENABLED = False
    except Exception as e:
        logger.warning(f"[MONITORING] Failed to initialize App Insights: {e}")
        _ENABLED = False
else:
    logger.info("[MONITORING] Azure Application Insights not configured (no connection string).")


# ── Public API ───────────────────────────────────────────

def is_monitoring_enabled() -> bool:
    """Check if Azure monitoring is active."""
    return _ENABLED


def track_event(name: str, properties: dict = None):
    """Track a custom event (e.g., 'diagnosis_completed', 'report_uploaded')."""
    if not _ENABLED or not _tracer:
        return
    try:
        with _tracer.span(name=name) as span:
            if properties:
                for k, v in properties.items():
                    span.add_attribute(k, str(v))
    except Exception as e:
        logger.debug(f"[MONITORING] Event tracking failed: {e}")


def track_exception(exception: Exception, properties: dict = None):
    """Track an exception for error alerting."""
    if not _ENABLED:
        return
    try:
        from opencensus.ext.azure.log_exporter import AzureLogHandler

        az_logger = logging.getLogger("cura3.errors")
        if not any(isinstance(h, AzureLogHandler) for h in az_logger.handlers):
            handler = AzureLogHandler(connection_string=_CONNECTION_STRING)
            az_logger.addHandler(handler)

        props = {"custom_dimensions": properties or {}}
        az_logger.exception(str(exception), extra=props)
    except Exception as e:
        logger.debug(f"[MONITORING] Exception tracking failed: {e}")


def track_duration(operation_name: str):
    """
    Decorator to track the duration of an async function.

    Usage:
        @track_duration("diagnosis_pipeline")
        async def run_diagnosis(...):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time()
            try:
                result = await func(*args, **kwargs)
                duration = (time() - start) * 1000  # ms
                track_event(
                    f"{operation_name}_completed",
                    {"duration_ms": round(duration, 2), "status": "success"},
                )
                return result
            except Exception as e:
                duration = (time() - start) * 1000
                track_event(
                    f"{operation_name}_failed",
                    {"duration_ms": round(duration, 2), "status": "error", "error": str(e)[:200]},
                )
                track_exception(e, {"operation": operation_name})
                raise

        return wrapper

    return decorator
