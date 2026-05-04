# Export contracts

## Delta development brief

Use this structure for `EXPORT CHANGES`.

```markdown
# Development Brief: Architecture Change Request

## 1. Brief Metadata
- Project: ...
- Generated: ...
- Source: architecture editor change log
- Change Count: ...

## 2. Change Summary
| Type | Target | Component | Summary |
|---|---|---|---|

## 3. Surgical Edit Instructions
### Change 1: ...
- Type: add | modify | delete | reroute | deprecate
- Target: node | edge | api | flow | schema | notes | tags
- Component: ...
- Before: ...
- After: ...
- Required implementation: ...
- Expected behavior after implementation: ...

## 4. Affected Architecture Objects
### Components
### Endpoints
### Schemas
### Flows
### Edges / Dependencies

## 5. Implementation Guidance for Coding Agent
- Locate affected files: ...
- Search terms: ...
- Update contracts: ...
- Preserve backwards compatibility: ...
- Remove or deprecate old behavior: ...

## 6. Acceptance Criteria
- [ ] ...

## 7. Verification Plan
- Unit tests: ...
- Integration tests: ...
- Contract/API tests: ...
- Manual checks: ...

## 8. Non-Goals
- ...

## 9. Open Questions and Assumptions
- ...
```

## Full architecture snapshot

Use this invariant structure for `EXPORT ALL STATES`.

```markdown
# Architecture Snapshot: PROJECT

## 0. Header Block
- Project: ...
- Domain: ...
- Repo: ...
- Generated: ...
- Nodes: ...
- Edges: ...
- Endpoints: ...

## Table of Contents
1. Introduction & Goals
2. Constraints
3. Context & Scope
4. Solution Strategy
5. Building Block View
6. Runtime View - User Flows
7. API Reference
8. Module Catalogue
9. Glossary
10. Architecture Flows

## 1. Introduction & Goals

## 2. Constraints

## 3. Context & Scope
```mermaid
flowchart LR
```

## 4. Solution Strategy

## 5. Building Block View
```mermaid
flowchart TD
```

## 6. Runtime View - User Flows

## 7. API Reference
### 7.1 Endpoint Index
| Method | Path | Module | Description |
|---|---|---|---|

### 7.2 Endpoint Details

## 8. Module Catalogue
| Module | Type | Responsibility | Tags | Notes |
|---|---|---|---|---|

## 9. Glossary
| Term | Meaning |
|---|---|

## 10. Architecture Flows

### Flow: source-service → target-service
- Source: source-service
- Target: target-service
- Method: POST
- Path: /v1/resource
- Description: Short service-to-service call purpose
- Critical: true
```

## Endpoint detail template

```markdown
### METHOD /path
- Module: module-id
- Description: ...
- Parameters:
  - ...
- Consumers:
  - ...
- Auth: ...
- Status: ...

Request schema:
```json
{}
```

Response schema:
```json
{}
```
```

## Architecture flow export rules

The `Architecture Snapshot` export must end with `## 10. Architecture Flows`. This section lists concrete service-to-service calls derived from `edges[]` plus matching target endpoint metadata.

Include only real calls between architecture services. Exclude:
- internal Ollama or local model calls;
- static file accesses;
- `/static/`, `/assets/`, `file:` or filesystem reads;
- pure ownership, deployment, UI-only, or documentation edges.

Each flow entry must contain exactly:
- `Source`;
- `Target`;
- `Method`;
- `Path`;
- `Description`;
- `Critical`.

Sort flows by `Source`, then `Target`, then `Path`, then HTTP method. Mark `Critical: true` when the edge or matched endpoint has `critical: true`, or when the edge is the primary API-call path for the runtime. Use `Critical: false` for supporting, non-blocking, or optional service-to-service calls.
