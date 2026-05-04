# Editable HTML architecture behavior

## Interface regions

A generated editor should contain:

1. Header with project name, mode controls, import/export buttons.
2. Legend for node types and edge styles.
3. Canvas for nodes and SVG edges.
4. Right detail panel for selected node.
5. Modal or textarea-based export surface.
6. Toast or status area for save/export feedback.

## Required controls

- `EDIT MODE`: toggles mutating controls.
- `ADD NODE`: creates a new node with stable ID validation.
- `EXPORT DATA`: downloads the full model JSON.
- `IMPORT DATA`: loads a model JSON.
- `SAVE`: stores the current model in browser localStorage.
- `LOAD`: restores from localStorage.
- `EXPORT CHANGES`: creates markdown delta dev brief.
- `EXPORT ALL STATES`: creates full architecture snapshot markdown.
- `EXPORT HTML`: downloads the current single-file editor with embedded model.

## Node editing

Support editing:
- label;
- sub;
- detail title;
- detail subtitle;
- tags;
- notes;
- constraints;
- risks;
- flow steps;
- API routes;
- schemas as JSON text where practical;
- position x/y.

Every save action must call `recordChange()` with `before` and `after` values.

## API editing

Support method, path, description, params, request schema, response schema, auth, status, and consumers.

Endpoint changes must be treated as surgical architecture changes. The generated brief must explicitly say whether the endpoint is:
- added;
- modified;
- removed;
- deprecated;
- redirected/rerouted.

## Edge editing

Support:
- adding an edge;
- deleting an edge;
- changing `from`;
- changing `to`;
- changing relation/style/label/protocol/data.

When an edge is rerouted, record it as `type: reroute`, `target: edge` and preserve previous `from`/`to`.

## Export behavior

### EXPORT CHANGES

Creates a delta development brief from `changes[]` only. If `changes[]` is empty, show an empty-state message and do not fabricate work.

### EXPORT ALL STATES

Creates a full architecture snapshot from the current model, not only changes.

### EXPORT DATA

Downloads raw JSON with `project`, `nodes`, `edges`, and `changes`.

## Determinism

- Keep section headings stable.
- Sort nodes by `id` in markdown exports unless runtime order is explicitly provided.
- Sort edges by `from`, then `to`, then `relation`.
- Sort endpoints by `path`, then `method`.
- Use ISO timestamps.

## Live API health-check behavior

When the generated HTML includes live API checking:

1. Show a `CHECK LIVE API` button in the header.
2. Ask for the health-check server URL when no `model.project.healthCheckUrl` exists.
3. Build checks from every node's `detail.apis[]` entries.
4. Send the checks to `POST /probe-architecture` on the health-check server.
5. Store the normalized response in `model.health`.
6. Add one change-log entry with `type: "probe"`, `target: "architecture-health"`, and the full health report as `after`.
7. Color node cards and endpoint rows from `model.health.nodes[nodeId]`.
8. Color edges by the worst status of their source and target nodes.
9. Never send browser-only secrets. Authentication belongs either in the server configuration or in an explicit bearer token option controlled by the operator.
10. On probe failure, keep the current model unchanged except for a visible browser error alert.
