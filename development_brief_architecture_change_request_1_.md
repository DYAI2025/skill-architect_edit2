# Development Brief: Architecture Change Request

## 1. Brief Metadata

Project: `skill-architect_edit2` / Omni Architecture Brief Engine

Target repository area: architecture editor generator and runtime validation environment

Source: observed failure in generated `astro-noctum-architecture-editor.html`

Change Count: 2

Generated: 2026-05-04T00:00:00+02:00

Context: The generated editor must render nodes, edges, detail panel, endpoint rows, and export controls from `architecture.json`. This is required editor behavior.

## 2. Change Summary

TypeTargetComponentSummary

fixgenerator/html-runtime`scripts/generate_architecture_editor.py`Repair generated JavaScript syntax error that prevents the editor from rendering any nodes, edges, or endpoints.

featureskill-runtime/devopsPlaywright + VPS health-check setupAdd browser-based validation capability and documented VPS deployment path for server-mediated API probing via `POST /probe-architecture`.

## 3. Surgical Edit Instructions

### Change 1: Fix generated HTML JavaScript parse failure

Type: fix

Target: generated HTML editor runtime

Component: `scripts/generate_architecture_editor.py`

#### Problem

The generated HTML can embed invalid JavaScript. In the observed broken editor, this function contained a raw multiline string in single quotes:

JavaScript

`function deviationBrief(){
  ...
  if(!rows.length)return '# Development Brief: No Deviations

No deviations available.';
  ...
}`

That is invalid JavaScript. The browser aborts parsing the full `<script>` block before `render()` runs. Result:

no node cards;

no SVG edges;

no API rows;

no detail panel hydration;

no export buttons with working logic.

#### Required implementation

Replace any generated raw multiline JavaScript string literals with template literals or escaped `\n` strings.

Recommended patch shape:

JavaScript

`function deviationBrief() {
  const d = model.deviations || {};
  const n = d.nodes || {};
  const e = d.edges || {};
  const rows = [];

  Object.entries(n).forEach(([id, v]) => rows.push(`- Node ${id}: ${v.message}`));
  Object.entries(e).forEach(([id, v]) => rows.push(`- Edge ${id}: ${v.message}`));

  if (!rows.length) {
    return `# Development Brief: No Deviations

No deviations available.`;
  }

  return `# Development Brief: Architecture Deviations

## Summary
${d.summary?.message || ''}

## Deviations
${rows.join('\n')}

## Implementation Order
- Fix each deviation exactly at the referenced node/edge.
- Add or correct missing endpoints/connections.
- Run VALIDATE ARCH again until no red deviation remains.

## Acceptance Criteria
- [ ] All red deviations are fixed.
- [ ] Validation reports "No deviations found".`;
}`

#### Additional hardening

Do not rely on browser-created global variables from DOM IDs such as `data`, `title`, `scene`, `panel`, or `modalText`.

Add explicit DOM references near the top of the runtime script:

JavaScript

`const dom = {
  data: document.getElementById('data'),
  title: document.getElementById('title'),
  scene: document.getElementById('scene'),
  lines: document.getElementById('lines'),
  panel: document.getElementById('panel'),
  modal: document.getElementById('modal'),
  modalTitle: document.getElementById('modalTitle'),
  modalText: document.getElementById('modalText'),
  editBtn: document.getElementById('editBtn')
};

let model = JSON.parse(dom.data.textContent);`

Then replace implicit references:

JavaScript

`title.textContent = ...
scene.querySelectorAll(...)
panel.innerHTML = ...
modalText.value = ...`

with:

JavaScript

`dom.title.textContent = ...
dom.scene.querySelectorAll(...)
dom.panel.innerHTML = ...
dom.modalText.value = ...`

#### Expected behavior after implementation

Opening the generated single-file HTML should immediately render:

all nodes from `model.nodes[]`;

all valid edges from `model.edges[]`;

node detail panel on click;

endpoint rows from `node.detail.apis[]`;

export controls for JSON, changes, and full snapshot.

The model shape must continue to follow the architecture contract: `project`, `nodes[]`, `edges[]`, and `changes[]`.

---

### Change 2: Add Playwright validation and VPS health-check feature

Type: feature

Target: validation/runtime environment

Component: skill environment, CI/dev tooling, optional VPS server

#### Required implementation: Playwright browser validation

Add a browser-based smoke test for generated HTML editors.

Required test capabilities:

Open generated `architecture-editor.html` via local file URL or static HTTP server.

Assert that no page-level JavaScript parse/runtime error occurs.

Assert visible node count is greater than zero.

Assert SVG edge paths are rendered.

Click at least one node.

Assert detail panel contains API rows when the selected node has `detail.apis[]`.

Assert `EXPORT DATA`, `EXPORT CHANGES`, and `EXPORT ALL STATES` buttons exist.

Suggested test file:

`tests/editor-render.spec.ts`

Suggested test logic:

TypeScript

`import { test, expect } from '@playwright/test';
import path from 'node:path';

test('generated architecture editor renders nodes, edges, and endpoint panel', async ({ page }) => {
  const htmlPath = path.resolve('tmp/architecture-editor.html');

  const errors: string[] = [];
  page.on('pageerror', err => errors.push(err.message));
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  await page.goto(`file://${htmlPath}`);

  await expect(page.locator('.node')).not.toHaveCount(0);
  await expect(page.locator('svg path')).not.toHaveCount(0);

  await page.locator('.node').first().click();
  await expect(page.locator('#panel')).toBeVisible();

  await expect(page.getByRole('button', { name: /EXPORT DATA/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /EXPORT CHANGES/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /EXPORT ALL STATES/i })).toBeVisible();

  expect(errors).toEqual([]);
});`

Required package additions:

JSON

`{
  "devDependencies": {
    "@playwright/test": "Unknown - search required"
  },
  "scripts": {
    "test:editor": "playwright test tests/editor-render.spec.ts"
  }
}`

Do not pin a version without checking the current repository package manager and lockfile.

#### Required implementation: VPS health-check server setup

The generated editor must not directly probe arbitrary APIs from the browser. Runtime health checks must be server-mediated through `POST /probe-architecture`.

Use the existing FastAPI server contract as implementation basis:

`live_api_health_server.py`

The server already defines the required environment variables:

`HEALTHCHECK_BASE_URL
HEALTHCHECK_ALLOWED_HOSTS
HEALTHCHECK_BEARER_TOKEN
HEALTHCHECK_UPSTREAM_TOKEN
HEALTHCHECK_TIMEOUT_SECONDS
HEALTHCHECK_CORS_ORIGINS`

and exposes:

`POST /probe-architecture`

with node, endpoint, and edge health aggregation.

Add repository documentation:

`docs/DEPLOY_HEALTHCHECK_VPS.md`

Minimum content:

Markdown

`# Deploy Architecture Healthcheck Server on VPS

## Purpose

Provide a controlled backend for architecture editor runtime checks.

## Security Requirements

- HTTPS only for public server URL.
- Bearer auth required for `/probe-architecture`.
- Strict `HEALTHCHECK_ALLOWED_HOSTS`.
- No browser-supplied secrets.
- Request timeout configured.
- CORS restricted to known editor origins.

## Install

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx certbot python3-certbot-nginx
python3 -m venv /opt/architecture-healthcheck/.venv
/opt/architecture-healthcheck/.venv/bin/pip install fastapi uvicorn httpx`

## Environment

Bash

`HEALTHCHECK_BASE_URL=https://api.example.com
HEALTHCHECK_ALLOWED_HOSTS=api.example.com,staging.example.com
HEALTHCHECK_BEARER_TOKEN=replace-with-server-token
HEALTHCHECK_UPSTREAM_TOKEN=replace-with-upstream-token-if-needed
HEALTHCHECK_TIMEOUT_SECONDS=10
HEALTHCHECK_CORS_ORIGINS=https://trusted-editor-origin.example.com`

## Run

Bash

`/opt/architecture-healthcheck/.venv/bin/uvicorn live_api_health_server:app --host 127.0.0.1 --port 8000`

## Systemd

Create `/etc/systemd/system/architecture-healthcheck.service`.

## Nginx

Reverse proxy HTTPS traffic to `127.0.0.1:8000`.

## Editor Usage

Use the generated editor's `CHECK LIVE API` button and enter:

`https://healthcheck.example.com`

The editor will call:

`POST https://healthcheck.example.com/probe-architecture`

`The generated editor already expects this endpoint shape for live health overlays. :contentReference[oaicite:4]{index=4}

## 4. Affected Architecture Objects

### Components

- `scripts/generate_architecture_editor.py`
- generated single-file HTML editor
- `live_api_health_server.py`
- Playwright test runner environment
- optional VPS runtime for health checks

### Endpoints

- `POST /probe-architecture`

### Schemas

Affected schemas:

- architecture model root: `project`, `nodes[]`, `edges[]`, `changes[]`
- endpoint probe object: `nodeId`, `endpointIndex`, `method`, `path`, `url`, `headers`, `query`, `body`, `expectedStatus`, `expectedResponse`
- health response: `timestamp`, `summary`, `nodes`, `edges`

These are defined by the model and live-health contracts. :contentReference[oaicite:5]{index=5} :contentReference[oaicite:6]{index=6}

### Flows

- HTML editor loads embedded `architecture.json`.
- HTML editor calls `render()`.
- `render()` draws nodes and SVG edges.
- User selects node.
- Detail panel renders flows and API routes.
- Optional: user clicks `CHECK LIVE API`.
- HTML editor sends checks to health server.
- Health server probes allowlisted upstream APIs.
- Health result colors nodes, endpoints, and edges.

### Edges / Dependencies

- `generate_architecture_editor.py` → generated HTML
- generated HTML → local browser runtime
- generated HTML → `POST /probe-architecture`
- health-check server → allowlisted upstream API hosts

## 5. Implementation Guidance for Coding Agent

- Locate affected files:
  - `scripts/generate_architecture_editor.py`
  - `references/editor-behavior.md`
  - `references/live-api-health-check.md`
  - `live_api_health_server.py` or equivalent server source path
  - `package.json` / lockfile if Playwright is added
- Search terms:
  - `function deviationBrief`
  - `No Deviations`
  - `No deviations available`
  - `document.getElementById`
  - `callLiveApiHealthCheck`
  - `/probe-architecture`
- Update contracts:
  - preserve `architecture.json` schema;
  - preserve export buttons;
  - preserve `## 10. Architecture Flows` in snapshot export;
  - preserve server-mediated health-check rule.
- Preserve backwards compatibility:
  - existing generated architecture JSON files must still load;
  - older models without `health`, `deviations`, or `expectedArchitecture` must still render.
- Remove or deprecate old behavior:
  - remove generated raw multiline single-quoted JS strings;
  - avoid implicit DOM globals.

## 6. Acceptance Criteria

- [ ] `python -m py_compile scripts/generate_architecture_editor.py` passes.
- [ ] Generator creates a single-file HTML editor from a sample `architecture.json`.
- [ ] Generated HTML JavaScript passes syntax validation with `node --check` or equivalent extraction check.
- [ ] Opening the generated HTML renders at least one `.node`.
- [ ] SVG edge paths render for valid `edges[]`.
- [ ] Clicking a node opens detail panel content.
- [ ] API rows render when `detail.apis[]` is non-empty.
- [ ] `EXPORT DATA`, `EXPORT CHANGES`, and `EXPORT ALL STATES` remain available.
- [ ] Playwright smoke test exists and fails on JavaScript parse errors.
- [ ] Health-check server documentation includes HTTPS, auth, allowlist, timeout, CORS, and no-secret rules.
- [ ] `/probe-architecture` behavior remains compatible with the documented OpenAPI contract. :contentReference[oaicite:7]{index=7}

## 7. Verification Plan

### Unit / static checks

```bash
python -m py_compile scripts/generate_architecture_editor.py`

Generate a test editor:

Bash

`python scripts/generate_architecture_editor.py \
  --input assets/sample-architecture.json \
  --output tmp/architecture-editor.html`

Extract and syntax-check generated JS:

Bash

`node --check tmp/generated-editor-script.js`

### Browser smoke test

Bash

`npm run test:editor`

Expected result:

no page errors;

`.node` count > 0;

`svg path` count > 0;

detail panel visible after node click;

export buttons visible.

### Health-check server test

Run locally:

Bash

`HEALTHCHECK_BASE_URL=https://api.example.com \
HEALTHCHECK_ALLOWED_HOSTS=api.example.com \
HEALTHCHECK_BEARER_TOKEN=test-token \
uvicorn live_api_health_server:app --host 127.0.0.1 --port 8000`

Probe with a controlled test request:

Bash

`curl -X POST http://127.0.0.1:8000/probe-architecture \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"checks":[{"nodeId":"service","endpointIndex":0,"method":"GET","path":"/health","expectedStatus":[200]}]}'`

Do not use private/internal target hosts unless explicitly allowlisted.

## 8. Non-Goals

Do not change the architecture model schema.

Do not change the visual design unless required for the render fix.

Do not add browser-side arbitrary URL probing.

Do not store API tokens in generated HTML or `architecture.json`.

Do not invent upstream endpoints for Astro-Noctum or any other analyzed repo.

Do not make Playwright a production dependency.

Do not run live API checks without a controlled server and allowlist.

## 9. Open Questions and Assumptions

`scripts/generate_architecture_editor.py` is the canonical generator path, based on the repository description.

Package manager is `Unknown - search required`; inspect `package.json`, `package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock` before adding Playwright.

CI provider is `Unknown - search required`; add GitHub Actions only if the repository already uses it or the maintainer approves.

VPS OS is assumed to be Ubuntu/Debian-like; adapt commands if the target server uses another distribution.

Public health-check hostname, TLS certificate domain, upstream API base URL, and allowed hosts are `Unknown - search required`.

Secrets must be configured only via server environment variables, never in editor HTML or architecture JSON
