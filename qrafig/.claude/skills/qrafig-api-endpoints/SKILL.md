---
name: qrafig-api-endpoints
description: Add or change a QRAFIG HTTP endpoint correctly — endpoint modules and route conventions, FluentValidation, RFC 9457 Problem Details with stable machine-readable codes, the fixed and load-bearing middleware order, idempotency keys, cursor pagination, OpenAPI declarations, API versioning, rate limiting and health. Use for any new route, contract change, validation rule, error code or middleware change on the backend API.
when_to_use: "Add an endpoint", changing a request or response contract, a new error code, validation, OpenAPI, idempotency, pagination, rate limits, middleware ordering, health checks.
---

# QRAFIG API endpoints

## Read first

- `backend/src/Qrafig.Api/Endpoints/` — the module file for your area, and the nearest existing
  endpoint that does something similar. QRAFIG is highly patterned; copy the neighbour.
- `backend/src/Qrafig.Api/Endpoints/EndpointConventions.cs` — the OpenAPI helpers every endpoint uses.
- `backend/src/Qrafig.Application/Common/ErrorCodes.cs` — the released codes.
- `backend/src/Qrafig.Api/Errors/ProblemDetailsMiddleware.cs`,
  `backend/src/Qrafig.Api/Validation/ValidationFilter.cs`,
  `backend/src/Qrafig.Api/Idempotency/IdempotencyFilter.cs`.
- `backend/src/Qrafig.Application/Common/Paging.cs`.
- `docs/implementation-status.md` → `## Endpoint inventory`.
- ADRs 0009, 0011, 0016, 0017, 0020, 0021, 0022, 0074, 0103, 0169.

## Shape of a new endpoint

1. **Put it in the existing module file** under `Endpoints/`, grouped with its neighbours. Not a new
   file per endpoint, and not a shared `Endpoints.cs` (ADR-0017).
2. **Resolve the tenant context first** — `RequireAsync` / `RequireWritableAsync`. There is no path
   that queries tenant data without one (ADR-0021).
3. **Name a permission code**, never a role name (ADR-0022).
4. **Take a request contract, return a response contract.** EF entities never leave the Application
   layer. A till is told what a till needs, and the wire is where that is decided (ADR-0169) — do not
   ship a field a client has no business having (cost price, row version, internal ids, credentials).
5. **Validate** with FluentValidation in `Qrafig.Application/Validation` (API-shape validators live in
   `Api/Validation/ApiContractValidators.cs`). The pipeline turns failures into `VALIDATION_FAILED`
   with per-field errors. **A validator may not dereference the field it has just rejected**
   (ADR-0168).
6. **Declare the contract in OpenAPI** with the `EndpointConventions` helpers —
   `ProducesValidationProblem`, `ProducesNotFound`, `ProducesConflict`, `ProducesUnauthorized`,
   `ProducesForbidden`, and `WithIdempotencyKeyHeader` on command endpoints. `OpenApiTests` enforces
   that implemented endpoints carry success and error schemas.
7. **Version by URL segment** — `/api/v1/…` (`Configuration/ApiOptions.cs`).

## Errors

Every error is RFC 9457 `application/problem+json` and carries a **stable machine-readable `code`**:

```json
{ "type": "https://errors.qrafig.com/VALIDATION_FAILED", "title": "Validation failed", "status": 400,
  "code": "VALIDATION_FAILED", "correlationId": "…", "traceId": "…",
  "errors": [{ "field": "email", "code": "INVALID_EMAIL", "message": "…" }] }
```

- Clients branch on `code`, **never** on `title` or `detail` — wording and localization change.
- A code never changes meaning once released (ADR-0009). Add a new one rather than repurposing one.
- Add it to `ErrorCodes.cs`, and to the Desktop client's mirror if a client branches on it —
  `MirroredContractTests` will fail otherwise.
- Status choice: `404` for a non-member (never `403`), `403 MISSING_PERMISSION` for a member without
  the permission, `409 CONCURRENCY_CONFLICT` for a stale `rowVersion`, `409` for a business refusal
  that is not the caller's fault to retry, `400` for a malformed or invalid request.

## Idempotency (ADR-0011)

Command endpoints accept an optional `Idempotency-Key` header. Retrying with the same key returns the
original response with `Idempotent-Replay: true`. Reusing a key with a **different body** returns
`409 IDEMPOTENCY_KEY_REUSED`. A command that **failed releases its key**, so the client can correct
the request and retry.

The key belongs to an **intent**, not to an attempt (ADR-0141, ADR-0148, ADR-0155, ADR-0162). A client
that composes a new key per retry executes twice. Where an outcome cannot be settled by the key, the
client asks the server rather than guessing.

## Middleware order — do not reorder casually (ADR-0020)

```
ForwardedHeaders → CorrelationId → ProblemDetails → SecurityHeaders
  → Routing → CORS → Authentication → Authorization → RateLimiter
  → IdempotencyBuffering → endpoints
```

Three constraints make it load-bearing:

1. **The rate limiter runs after routing and authentication** — endpoint-scoped policies need endpoint
   metadata and partitioning by user or device needs an authenticated principal. Earlier, only the
   global limiter takes effect and per-endpoint budgets are silently ignored.
2. **Idempotency buffering runs before the endpoint** — minimal-API model binding drains the body, so
   the fingerprint must be taken from a stream made rewindable earlier. Inside the endpoint filter it
   always hashes an empty body, which defeats reuse detection.
3. **Security headers are applied via `Response.OnStarting`** — an error path may rewrite the response
   before writing a Problem Details body. For the same reason the Problem Details writer never calls
   `Response.Clear()`; that discarded `Retry-After` on rate-limit rejections.

Each constraint is pinned by a test in `RateLimitAndHeaderTests` or `IdempotencyTests`.

## Pagination

Cursor pagination for large mutable collections; offset only for small stable sets (ADR-0016). An
**operational queue must be cursor-complete** — it walks to the end so unresolved work cannot be
buried — while a history list may be capped (ADR-0200). Give the ordering its composite index from the
start. A cursor must not be replayable across tenants.

## Bounded reads

A synchronous report or export is **bounded and says what to do about it** (ADR-0074, ADR-0192): count
before loading, and refuse with a named code rather than truncating. Truncation that looks like a
complete answer is the failure this prevents.

## Health and background work

`/health/live`, `/health/ready`, `/health/startup`. Jobs run on a background loop inside the API and
can be turned off with `Jobs:Enabled=false`; the endpoints still work with the loop off. The outbox
worker is `Outbox:Enabled=false`. Both are off in the integration suite.

## Verification

Success; validation failure; **403 missing permission**; **404 non-member**; **cross-tenant**; the
`409` paths your endpoint can produce; `OpenApiTests` green; an idempotency replay if the endpoint
takes a key; and a concurrency test if there is a read-modify-write.

## Do not

- Do not return an EF entity.
- Do not branch a client on `title` or `detail`.
- Do not change the meaning of a released code.
- Do not put a new endpoint in its own file or a new module for convenience.
- Do not return `403` to a non-member.
- Do not add a permanent public URL for a stored file — links expire.
- Do not truncate a bounded read silently.
- Do not reorder the middleware pipeline without reading ADR-0020 and running its tests.

## Related skills

`qrafig-tenancy` · `qrafig-authorization` · `qrafig-concurrency` · `qrafig-observability` ·
`qrafig-storage` · `qrafig-reporting` · `qrafig-testing`.
External: ASP.NET Core Web API engineering, Minimal API OpenAPI — see `docs/ai/sources.md`.
