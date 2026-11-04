# CONTEXT — pulse-dashboard

`pulse-dashboard` aggregates and renders incident summaries from `pulse-engine` alert streams.

## Responsibilities
- Consume alert payloads conforming to `pulse-engine/alert-dispatch`.
- Group active alerts by severity and service, and render incident summary reports.
