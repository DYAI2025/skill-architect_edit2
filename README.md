# skill-architect_edit2

`skill-architect_edit2` is an architecture-editor generator for LLM-driven engineering workflows.
It turns architecture JSON into a single-file interactive HTML application that supports:

- architecture visualization,
- interactive structural edits,
- runtime health overlays,
- expected-vs-actual validation,
- development-brief export,
- full architecture snapshot export,
- and now a guarded **Auto-Improve** strategic suggestion workflow.

## 1) Repository Goal

The repository is designed to create a **practical architecture operating interface** rather than static documentation.
The generated editor should help teams:

1. understand current architecture quickly,
2. capture intentional architecture changes with auditability,
3. detect architecture drift and contradictions early,
4. generate implementation-ready briefs for coding agents.

## 2) Main Components

## 2.1 `scripts/generate_architecture_editor.py`

Core generator script. It:

- loads an input architecture model (or falls back to a built-in sample model),
- renders an embedded HTML/JS application template,
- writes a single portable `.html` output file.

### CLI

```bash
python scripts/generate_architecture_editor.py --input architecture.json --output architecture-editor.html
python scripts/generate_architecture_editor.py --output architecture-editor.html
```

## 2.2 `assets/sample-architecture.json`

Example architecture model that can be used as a base for experimentation.

## 2.3 `references/*`

Reference contracts and behavior documentation for architecture model shape, editor behavior, and API health-check integration.

## 3) Data Model (High-Level)

The editor expects (at minimum):

- `project`
- `nodes[]`
- `edges[]`
- `changes[]`

Optional advanced blocks include:

- `health`
- `deviations`
- `expectedArchitecture`
- `autoImprove`
- `devBriefs`

## 4) Generated Editor Features

## 4.1 Visualization and Editing

- node/edge rendering on a canvas,
- detail panel per node,
- edit mode with tracked changes,
- add/edit/delete flow steps,
- add/edit/delete API routes,
- add/delete nodes,
- add/reroute/delete edges.

All user-driven structural edits are recorded with `origin: "user-edit"` for governance and session policy checks.

## 4.2 Change Tracking and Export

- change log with before/after payloads,
- **Development Brief** export (`EXPORT CHANGES`),
- full architecture markdown snapshot export (`EXPORT ALL STATES`).

## 4.3 Health Overlay

- server-mediated live probing via `POST /probe-architecture`,
- endpoint and node statuses (`red`, `yellow`, `green`, `unknown`),
- edge coloration based on health/dependency status.

## 4.4 Architecture Validation

- compares `expectedArchitecture` with currently rendered model,
- marks mismatches as deviations,
- supports global and node-specific deviation brief creation.

## 4.5 Auto-Improve (New)

Two new buttons in the generated editor:

- `AUTO-IMPROVE`: evaluates and proposes one strategic improvement,
- `CONFIRM AI`: confirms the pending proposal and converts it into a dev brief.

### Auto-Improve Policy Guards

Auto-Improve can run only when:

1. **No user-requested changes** have already been made in the current session (`origin: "user-edit"` lock), and
2. **No prior Auto-Improve** exists for the active dev brief context (neither as pending proposal nor as confirmed history).

This enforces:

- low contradiction risk against manually requested changes,
- one strategic recommendation per brief (strictly enforced across pending + history),
- traceable proposal lifecycle.

### Auto-Improve Output

The proposal includes:

- title,
- strategic goal context,
- impact rationale,
- effort estimate,
- scoped implementation steps,
- risk assessment,
- mitigation plan,
- success metrics.

When confirmed, a structured auto-improve dev brief is created and added to `model.devBriefs`.

## 5) Risk Evaluation for Auto-Improve

## 5.1 Key Risks

1. **Contradictions with in-session intent** if user changes already started.
2. **Overfitting to incomplete architecture data** (missing APIs/constraints).
3. **Short-term optimization bias** (impulsive proposals with weak strategic relevance).
4. **Operational false positives** when enforcement enters CI too aggressively.

## 5.2 Implemented Mitigations

- hard gate against sessions with existing `user-edit` changes,
- one-trigger-per-dev-brief policy,
- explicit risk section in every proposal,
- mandatory mitigation list and success metrics,
- confirmation step before promotion to dev brief.

## 5.3 Recommended Additional Mitigations

- introduce a configurable confidence score threshold,
- require baseline freshness checks (`expectedArchitecture` updated recently),
- add human-owner field for accepted auto-improve items,
- enforce contradiction checks on later changes against confirmed auto-improve intent.

## 6) Bug Fixes and Hardening Included

1. **Session-aware edit origin tagging** added to structural edit change events.
2. **Deviation brief text consistency** improved (English headings/instructions).
3. **Strategic workflow coverage** expanded with proposal + confirmation lifecycle.
4. **One-trigger guard strengthened** so Auto-Improve is blocked when either a pending proposal or a confirmed history entry exists for the same `devBriefId`.
5. **Operator-facing block message improved** to include the concrete `devBriefId` and blocking reason.

## 7) Local Validation Steps

Run these checks after modifying the script:

```bash
python -m py_compile scripts/generate_architecture_editor.py
python scripts/generate_architecture_editor.py --input assets/sample-architecture.json --output /tmp/architecture-editor.html
```

Then open the generated HTML in a browser and test:

- normal edit mode,
- validation and deviation export,
- auto-improve (before any user edits),
- lock behavior after a user edit.

## 8) Notes for Integrators

- Keep secrets out of architecture JSON and HTML.
- Route runtime checks through a controlled backend.
- Treat confirmed Auto-Improve briefs as strategic constraints for subsequent architecture changes.
