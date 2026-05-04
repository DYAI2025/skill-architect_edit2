# Live API health check extension

## Purpose

The editor can call a user-operated health-check server and color architecture nodes, endpoint rows, and connected edges by runtime status.

## Status semantics

| Status | Meaning | UI color |
|---|---|---|
| `green` | The endpoint completed with an expected HTTP status and no detected request/response mismatch. | green |
| `yellow` | The endpoint was reachable but showed a partial problem: unexpected 4xx, validation mismatch, missing expected response field, malformed request sample, or mixed endpoint results inside the same node. | yellow |
| `red` | The endpoint or node is functionally broken: network failure, timeout, DNS/TLS failure, 5xx, unhandled exception, or every endpoint in the node failed. | red |
| `unknown` | The endpoint was not checked or the health-check response did not contain enough information. | neutral |

Node status is derived from endpoint status:
- red when all checked endpoints under the node are red or when the server reports the node as red;
- yellow when at least one endpoint is yellow or when results are mixed;
- green when every checked endpoint is green;
- unknown when no endpoint was checked.

Edges are colored by the worst status of their connected nodes.

## Model fields for endpoint probes

Each `detail.apis[]` entry can include these optional probe fields:

```json
{
  "method": "GET",
  "path": "/api/example",
  "url": "",
  "headers": { "X-Demo": "true" },
  "query": { "id": "123" },
  "body": null,
  "expectedStatus": [200, 204],
  "expectedResponse": {
    "requiredJsonPaths": ["data.id", "data.status"]
  }
}
```

Rules:
- Use `url` for an absolute endpoint URL only when the endpoint does not belong to the configured base URL.
- Prefer `path` plus the server-side `HEALTHCHECK_BASE_URL` for normal checks.
- Store only non-secret demo headers in the model. Secrets belong on the server, not in the generated HTML.
- Use `expectedResponse.requiredJsonPaths` for lightweight response-contract checks.

## HTML function contract

The generated HTML contains:

```javascript
async function callLiveApiHealthCheck(serverUrl, options = {})
```

It sends:

```json
{
  "project": {},
  "nodes": [],
  "edges": [],
  "checks": [
    {
      "nodeId": "service",
      "endpointIndex": 0,
      "method": "GET",
      "path": "/api/example",
      "url": "",
      "headers": {},
      "query": {},
      "body": null,
      "expectedStatus": [200, 201, 202, 204],
      "expectedResponse": null
    }
  ]
}
```

It expects either a nested report:

```json
{
  "timestamp": "2026-05-03T12:00:00Z",
  "summary": { "status": "yellow", "green": 4, "yellow": 1, "red": 0, "unknown": 0 },
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
```

or a flat `results[]` array with `nodeId`, `endpointIndex`, `status`, `summary`, `httpStatus`, and `latencyMs`.

## Security requirements

Do not let the health-check server call arbitrary internal hosts. Use an allowlist.

Required production controls:
- HTTPS only for the public server URL.
- Authentication for `/probe-architecture`.
- Host allowlist for every resolved request URL.
- Request timeout.
- Maximum request body size.
- No browser-supplied secrets forwarded blindly.
- CORS restricted to known origins when the HTML editor calls the server directly.

## Flow testing extension

The HTML editor sends both endpoint checks and extracted architecture flows to `POST /probe-architecture`. A flow check contains:

```json
{
  "source": "whatsorga-ingest",
  "target": "backlog-core",
  "flowIndex": 0,
  "nodeId": "backlog-core",
  "method": "POST",
  "path": "/v1/inputs",
  "description": "Submits normalized input_event",
  "critical": true,
  "expectedStatus": [200, 201, 202, 204]
}
```

The server returns edge health under `edges` keyed as `source->target`:

```json
{
  "edges": {
    "whatsorga-ingest->backlog-core": {
      "status": "green",
      "summary": "1/1 flows passed",
      "flows": [
        { "index": 0, "method": "POST", "path": "/v1/inputs", "critical": true, "status": "green" }
      ]
    }
  }
}
```

Use the same color semantics for edges as for nodes and endpoints: `red` means the flow is functionally broken, `yellow` means partial/contract mismatch, `green` means the flow passed, and `unknown` means not checked.
