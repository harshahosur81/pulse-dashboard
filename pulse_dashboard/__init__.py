"""pulse-dashboard package for aggregating and rendering alert-dispatch streams."""

from pulse_dashboard.summary import (
    REQUIRED_FIELDS,
    SEVERITY_ORDER,
    VALID_SEVERITIES,
    render_markdown_report,
    summarize_alerts,
    validate_alert,
)

__all__ = [
    "REQUIRED_FIELDS",
    "SEVERITY_ORDER",
    "VALID_SEVERITIES",
    "render_markdown_report",
    "summarize_alerts",
    "validate_alert",
]
