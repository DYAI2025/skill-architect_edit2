# Architecture model contract

Use this model whenever an architecture must be visualized, edited, exported, or handed off to a coding agent.

## Root object

```json
{
  "project": {
    "name": "Project name",
    "domain": "software | product | api | workflow | data | agent | mixed",
    "repo": "optional repository or workspace",
    "timestamp": "ISO-8601 timestamp",
    "description": "short architecture purpose"
  },
  "nodes": [],
  "edges": [],
  "changes": []
}
```

## Node object

```json
{
  "id": "stable-kebab-case-id",
  "x": 500,
  "y": 420,
  "type": "entry | ui | service | api | data | agent | workflow | external | security | infra | domain | custom",
  "icon": "◇",
  "label": "Short label",
  "sub": "short subtitle",
  "detail": {
    "title": "Full title",
    "subtitle": "layer · responsibility",
    "tags": ["api", "frontend"],
    "flow": ["step one", "step two"],
    "apis": [],
    "schemas": [],
    "notes": "implementation context",
    "constraints": [],
    "risks": []
  }
}
```

## API route object

```json
{
  "method": "GET",
  "path": "/api/resource/:id",
  "desc": "what the endpoint does",
  "params": ["userId: string", "date: ISO-8601"],
  "requestSchema": { "type": "object", "properties": {} },
  "responseSchema": { "type": "object", "properties": {} },
  "consumers": ["dashboard"],
  "auth": "unknown | public | session | bearer | service",
  "status": "planned | active | deprecated | removed"
}
```

## Edge object

```json
{
  "from": "source-node-id",
  "to": "target-node-id",
  "style": "primary | secondary | api | event | data | dependency | risk | ownership",
  "label": "optional edge label",
  "relation": "user-flow | api-call | event-flow | data-flow | dependency | deployment | ownership | risk-control",
  "protocol": "HTTP | queue | file | human | internal | unknown",
  "method": "optional HTTP method used for service-to-service calls",
  "path": "optional path used for service-to-service calls",
  "description": "optional short flow description",
  "critical": true,
  "data": "optional payload or domain object"
}
```

## Change object

```json
{
  "id": "c_stable_or_random",
  "timestamp": "ISO-8601 timestamp",
  "type": "modify | add | delete | reroute | deprecate",
  "target": "node | edge | api | flow | schema | notes | tags | constraint | risk",
  "nodeId": "optional-node-id",
  "edgeIndex": 0,
  "apiIndex": 0,
  "before": {},
  "after": {},
  "description": "human-readable exact edit"
}
```

## Normalization rules

- Use kebab-case IDs.
- Preserve original endpoint casing and path syntax.
- Use `Unknown - search required` instead of inventing file paths.
- Keep deleted nodes in the model with `_deleted: true` until export is complete so the brief can reference them.
- Sort endpoints by path, then method.
- Sort nodes by known runtime order, otherwise by layer, then label.

## Live API health extension

Endpoint entries in `detail.apis[]` may include optional probe metadata:

| Field | Meaning |
|---|---|
| `url` | Absolute URL for this endpoint when it cannot be derived from the server base URL. |
| `headers` | Non-secret request headers. Do not store tokens here. |
| `query` | Query parameters for the probe request. |
| `body` | JSON request body for POST, PUT, or PATCH probes. |
| `expectedStatus` | Accepted HTTP status codes. Default: `[200, 201, 202, 204]`. |
| `expectedResponse.requiredJsonPaths` | Dot-paths that must exist in a JSON response. |

The generated editor may store the latest runtime health report under top-level `health`:

```json
{
  "health": {
    "timestamp": "2026-05-03T12:00:00Z",
    "summary": { "status": "green", "green": 1, "yellow": 0, "red": 0, "unknown": 0 },
    "nodes": {
      "service": {
        "status": "green",
        "summary": "1/1 endpoints passed",
        "endpoints": [
          { "status": "green", "summary": "HTTP 200", "httpStatus": 200, "latencyMs": 84 }
        ]
      }
    },
    "edges": {}
  }
}
```

Status values are restricted to `green`, `yellow`, `red`, and `unknown`.

## Architecture flow extraction extension

The snapshot exporter derives `## 10. Architecture Flows` from edges that represent real service-to-service calls. Use one edge per meaningful runtime call when a source component invokes a target component. Prefer explicit edge fields (`method`, `path`, `description`, `critical`) when available. Otherwise, match the edge to a target endpoint in `target.detail.apis[]` using endpoint `consumers`, `method`, or `path`.

Rules:
- Include only service-to-service API, event, queue, gRPC, HTTP, HTTPS, or data-call flows.
- Exclude internal Ollama calls, static file access, filesystem reads, asset loads, and pure UI/documentation/deployment/ownership edges.
- Sort generated flows by source, target, path, and method.
- De-duplicate identical `source + target + method + path` entries.
- Every exported flow must include source, target, method, path, description, and criticality.

Example:

```json
{
  "from": "whatsorga-ingest",
  "to": "backlog-core",
  "style": "primary",
  "relation": "api-call",
  "protocol": "HTTP",
  "method": "POST",
  "path": "/v1/inputs",
  "description": "Submits normalized input_event",
  "critical": true
}
```
