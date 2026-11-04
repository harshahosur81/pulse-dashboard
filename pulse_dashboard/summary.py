"""Aggregation and Markdown reporting for pulse-engine/alert-dispatch v1 payloads."""

from __future__ import annotations

from typing import Any

REQUIRED_FIELDS: tuple[str, ...] = (
    "alert_id",
    "event_id",
    "source",
    "metric",
    "value",
    "threshold",
    "severity",
    "triggered_at",
    "summary",
)

STRING_FIELDS: tuple[str, ...] = (
    "alert_id",
    "event_id",
    "source",
    "metric",
    "severity",
    "triggered_at",
    "summary",
)

NUMBER_FIELDS: tuple[str, ...] = ("value", "threshold")

SEVERITY_ORDER: tuple[str, ...] = ("critical", "warning", "info")
VALID_SEVERITIES: frozenset[str] = frozenset(SEVERITY_ORDER)
_SEVERITY_RANK: dict[str, int] = {
    severity: idx for idx, severity in enumerate(SEVERITY_ORDER)
}


def _is_number(val: Any) -> bool:
    """Return True if val is an int or float (excluding bool)."""
    return isinstance(val, (int, float)) and not isinstance(val, bool)


def validate_alert(alert: dict[str, Any]) -> dict[str, Any]:
    """Validate an alert payload against the pulse-engine/alert-dispatch v1 contract.

    Args:
        alert: Raw dictionary representing a dispatched alert.

    Returns:
        A shallow copy of the validated alert dictionary.

    Raises:
        ValueError: If alert is not a dict, is missing required fields, has invalid
            field types, or specifies an unsupported severity.
    """
    if not isinstance(alert, dict):
        raise ValueError("Alert payload must be a dictionary.")

    missing = [field for field in REQUIRED_FIELDS if field not in alert or alert[field] is None]
    if missing:
        raise ValueError(f"Alert payload missing required fields: {', '.join(missing)}")

    for field in STRING_FIELDS:
        val = alert[field]
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"Field '{field}' must be a non-empty string.")

    for field in NUMBER_FIELDS:
        val = alert[field]
        if not _is_number(val):
            raise ValueError(f"Field '{field}' must be a number.")

    severity = alert["severity"]
    if severity not in VALID_SEVERITIES:
        raise ValueError(
            f"Invalid severity '{severity}'. Expected one of: {', '.join(SEVERITY_ORDER)}."
        )

    return dict(alert)


def summarize_alerts(alerts: list[dict[str, Any]]) -> dict[str, Any]:
    """Group and summarize validated alerts by severity and by source.

    Args:
        alerts: Sequence of alert dictionaries conforming to alert-dispatch v1.

    Returns:
        Dictionary containing:
            - total: Total number of alerts.
            - highest_severity: Highest severity present ('critical', 'warning', 'info', or None).
            - severity_counts: Mapping of each severity ('critical', 'warning', 'info') to count.
            - source_counts: Mapping of each source service to alert count.
            - by_severity: Mapping of each severity to its list of alerts.
            - by_source: Mapping of each source service to its list of alerts.
            - ordered_alerts: List of alerts ordered from highest to lowest severity.
            - summaries: List of alert summary strings ordered from highest to lowest severity.
    """
    validated = [validate_alert(alert) for alert in alerts]

    by_severity: dict[str, list[dict[str, Any]]] = {
        sev: [] for sev in SEVERITY_ORDER
    }
    by_source: dict[str, list[dict[str, Any]]] = {}

    for item in validated:
        by_severity[item["severity"]].append(item)
        source = item["source"]
        by_source.setdefault(source, []).append(item)

    severity_counts: dict[str, int] = {
        sev: len(by_severity[sev]) for sev in SEVERITY_ORDER
    }
    source_counts: dict[str, int] = {
        source: len(items) for source, items in by_source.items()
    }

    highest_severity: str | None = None
    for sev in SEVERITY_ORDER:
        if severity_counts[sev] > 0:
            highest_severity = sev
            break

    ordered_alerts: list[dict[str, Any]] = sorted(
        validated, key=lambda item: _SEVERITY_RANK[item["severity"]]
    )
    summaries: list[str] = [item["summary"] for item in ordered_alerts]

    return {
        "total": len(validated),
        "highest_severity": highest_severity,
        "severity_counts": severity_counts,
        "source_counts": source_counts,
        "by_severity": by_severity,
        "by_source": by_source,
        "ordered_alerts": ordered_alerts,
        "summaries": summaries,
    }


def render_markdown_report(alerts: list[dict[str, Any]]) -> str:
    """Render a clean Markdown status report from an alert-dispatch stream.

    Args:
        alerts: Sequence of alert dictionaries conforming to alert-dispatch v1.

    Returns:
        Formatted Markdown string summarizing overall status, severity breakdown,
        source breakdown, and ordered incident summaries.
    """
    summary = summarize_alerts(alerts)
    total = summary["total"]
    highest = summary["highest_severity"] or "none"

    lines: list[str] = [
        "# Pulse Incident Status Report",
        "",
        f"- **Total Alerts**: {total}",
        f"- **Highest Severity**: {highest}",
        "",
    ]

    if total == 0:
        lines.append("No active alerts.")
        return "\n".join(lines)

    lines.extend(
        [
            "## By Severity",
            "",
            f"- **critical**: {summary['severity_counts']['critical']}",
            f"- **warning**: {summary['severity_counts']['warning']}",
            f"- **info**: {summary['severity_counts']['info']}",
            "",
            "## By Source",
            "",
        ]
    )

    for source in sorted(summary["source_counts"]):
        count = summary["source_counts"][source]
        lines.append(f"- **{source}**: {count}")

    lines.extend(["", "## Active Alert Summaries", ""])
    for alert in summary["ordered_alerts"]:
        lines.append(
            f"- [{alert['severity'].upper()}] `{alert['source']}` "
            f"(`{alert['metric']}`={alert['value']} vs {alert['threshold']}): "
            f"{alert['summary']}"
        )

    return "\n".join(lines)
