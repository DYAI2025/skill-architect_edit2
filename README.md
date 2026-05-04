# skill-architect_edit2

A skill for GPT or Claude to visualize repository architecture, support interactive edits, validate expected vs rendered architecture, and export LLM-ready development briefs.

## Highlights
- Single-file HTML architecture editor generation (`scripts/generate_architecture_editor.py`).
- Health overlays for nodes/endpoints (red/yellow/green/unknown).
- **NEW:** Expected-vs-actual architecture validation with red deviation markers and per-node explanation.
- **NEW:** Deviation-to-dev-brief export (global and per-node).
- **NEW:** Visible legend explaining connection line styles and status semantics.
