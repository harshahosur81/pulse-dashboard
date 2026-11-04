<!-- generated-from: sha256:ca4a48784007e859 -->
<!-- shim-body-sha256: sha256:558b3b3f6c2b1bf9 -->
# Generated shim for pulse-dashboard (metabrain:pulse-platform)

Do not edit by hand; edit `CONTEXT.md` and re-run `metabrain init --brain`.

# CONTEXT — pulse-dashboard

`pulse-dashboard` aggregates and renders incident summaries from `pulse-engine` alert streams.

## Responsibilities
- Consume alert payloads conforming to `pulse-engine/alert-dispatch`.
- Group active alerts by severity and service, and render incident summary reports.
