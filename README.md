# pulse-dashboard

`pulse-dashboard` consumes structured alert payloads conforming to the `pulse-engine/alert-dispatch` v1 contract, aggregates active incidents by severity and service source, and renders Markdown incident summary reports.

## Structure

- `pulse_dashboard/summary.py` — Contract validation (`validate_alert`), alert stream aggregation (`summarize_alerts`), and Markdown report generation (`render_markdown_report`).
- `tests/test_summary.py` — Unit test suite verifying contract enforcement, multi-source/multi-severity grouping, empty stream handling, and report rendering.

## Running Tests

```bash
python3 -m unittest discover -s tests -t . -v
```
