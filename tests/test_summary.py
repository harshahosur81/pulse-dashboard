"""Unit tests for pulse_dashboard.summary."""

from __future__ import annotations

import unittest

from pulse_dashboard.summary import (
    render_markdown_report,
    summarize_alerts,
    validate_alert,
)


def _make_alert(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "alert_id": "alt-001",
        "event_id": "evt-001",
        "source": "payments-api",
        "metric": "latency_ms",
        "value": 450.0,
        "threshold": 300.0,
        "severity": "warning",
        "triggered_at": "2026-11-04T00:00:00Z",
        "summary": "payments-api latency_ms (450.0) breached threshold 300.0",
    }
    base.update(overrides)
    return base


class TestPulseDashboardSummary(unittest.TestCase):
    """Tests for alert-dispatch v1 contract validation, aggregation, and reporting."""

    def test_validate_alert_accepts_valid_payload(self) -> None:
        alert = _make_alert()
        validated = validate_alert(alert)
        self.assertEqual(validated, alert)
        self.assertIsNot(validated, alert)

    def test_validate_alert_rejects_missing_required_fields(self) -> None:
        alert = _make_alert()
        del alert["triggered_at"]
        with self.assertRaisesRegex(ValueError, "triggered_at"):
            validate_alert(alert)

    def test_validate_alert_rejects_invalid_severity(self) -> None:
        alert = _make_alert(severity="fatal")
        with self.assertRaisesRegex(ValueError, "Invalid severity 'fatal'"):
            validate_alert(alert)

    def test_validate_alert_rejects_non_numeric_value_or_threshold(self) -> None:
        with self.assertRaisesRegex(ValueError, "Field 'value' must be a number"):
            validate_alert(_make_alert(value="450"))
        with self.assertRaisesRegex(ValueError, "Field 'threshold' must be a number"):
            validate_alert(_make_alert(threshold=True))

    def test_summarize_alerts_empty_stream(self) -> None:
        result = summarize_alerts([])
        self.assertEqual(result["total"], 0)
        self.assertIsNone(result["highest_severity"])
        self.assertEqual(
            result["severity_counts"],
            {"critical": 0, "warning": 0, "info": 0},
        )
        self.assertEqual(result["source_counts"], {})
        self.assertEqual(result["summaries"], [])
        self.assertEqual(result["ordered_alerts"], [])

    def test_summarize_alerts_multi_source_and_multi_severity(self) -> None:
        alerts = [
            _make_alert(
                alert_id="alt-1",
                event_id="evt-1",
                source="auth-service",
                severity="info",
                summary="auth-service info alert",
            ),
            _make_alert(
                alert_id="alt-2",
                event_id="evt-2",
                source="payments-api",
                severity="critical",
                summary="payments-api critical alert",
            ),
            _make_alert(
                alert_id="alt-3",
                event_id="evt-3",
                source="payments-api",
                severity="warning",
                summary="payments-api warning alert",
            ),
        ]
        result = summarize_alerts(alerts)

        self.assertEqual(result["total"], 3)
        self.assertEqual(result["highest_severity"], "critical")
        self.assertEqual(
            result["severity_counts"],
            {"critical": 1, "warning": 1, "info": 1},
        )
        self.assertEqual(
            result["source_counts"],
            {"auth-service": 1, "payments-api": 2},
        )
        self.assertEqual(len(result["by_source"]["payments-api"]), 2)
        self.assertEqual(
            result["summaries"],
            [
                "payments-api critical alert",
                "payments-api warning alert",
                "auth-service info alert",
            ],
        )

    def test_render_markdown_report_with_active_alerts(self) -> None:
        alerts = [
            _make_alert(
                alert_id="alt-1",
                source="auth-service",
                metric="error_rate",
                value=0.08,
                threshold=0.05,
                severity="warning",
                summary="Auth error rate elevated",
            ),
            _make_alert(
                alert_id="alt-2",
                source="db-cluster",
                metric="cpu_pct",
                value=98,
                threshold=90,
                severity="critical",
                summary="DB CPU saturated",
            ),
        ]
        report = render_markdown_report(alerts)
        self.assertIn("# Pulse Incident Status Report", report)
        self.assertIn("- **Total Alerts**: 2", report)
        self.assertIn("- **Highest Severity**: critical", report)
        self.assertIn("- **critical**: 1", report)
        self.assertIn("- **warning**: 1", report)
        self.assertIn("- **auth-service**: 1", report)
        self.assertIn("- **db-cluster**: 1", report)
        self.assertLess(
            report.index("[CRITICAL] `db-cluster`"),
            report.index("[WARNING] `auth-service`"),
        )

    def test_render_markdown_report_empty_stream(self) -> None:
        report = render_markdown_report([])
        self.assertIn("- **Total Alerts**: 0", report)
        self.assertIn("- **Highest Severity**: none", report)
        self.assertIn("No active alerts.", report)


if __name__ == "__main__":
    unittest.main()
