---
name: qrafig-observability
description: Make QRAFIG diagnosable in production — OpenTelemetry traces and metrics for ASP.NET Core, HttpClient, Npgsql and the runtime, correlation and trace ids echoed on every response and pushed into the logging scope, structured JSON logging, redaction rules, the Qrafig.Outbox meter and job_runs visibility, and the Desktop rolling file log. Use when adding a metric, a span, a log line, a health signal, or when diagnosing something in a running system.
when_to_use: Adding telemetry, tracing a request end to end, correlation ids, log redaction, queue and job health, production diagnostics, "how do I see what happened".
---

# Observability in QRAFIG

## Read first

- `backend/src/Qrafig.Api/Observability/ObservabilitySetup.cs`,
  `backend/src/Qrafig.Api/Observability/CorrelationIdMiddleware.cs`.
- `backend/src/Qrafig.Api/Health/HealthSetup.cs`,
  `backend/src/Qrafig.Infrastructure/Health/ConnectivityHealthChecks.cs`.
- `desktop/src/Qrafig.Desktop/Logging/RollingFileLogger.cs`.
- Tests: `CorrelationIdTests`, `HealthTests`, `RateLimitAndHeaderTests`.

## What is already wired

- **Structured JSON logging** with scopes, UTC timestamps.
- **OpenTelemetry traces**: ASP.NET Core (with `/health` filtered out — probes are high-frequency and
  carry no diagnostic value as spans), HttpClient, **Npgsql**.
- **OpenTelemetry metrics**: ASP.NET Core, HttpClient, runtime.
- **OTLP exporter only when an endpoint is configured.** With none configured the instrumentation is
  still collected but no exporter is registered, so a missing collector cannot stall or fail the
  application. Preserve that property.
- **Correlation**: `X-Correlation-Id` is read from the request or minted (UUIDv7), echoed on the
  response alongside `X-Trace-Id`, set as the `qrafig.correlation_id` span tag, and pushed into the
  logging scope so every line of that request carries both. Both ids also appear in every Problem
  Details body.
- **Health**: `/health/live`, `/health/ready`, `/health/startup`, with PostgreSQL and Redis readiness
  checks written in-repo rather than pulled from third-party packages. Redis connects lazily so the
  API starts without it.
- **Outbox metrics** under the `Qrafig.Outbox` meter: backlog, oldest pending age, dead-letter
  backlog, counters for processed / retried / dead-lettered, and a per-handler duration histogram.
- **`job_runs`** rows written *before* the work and completed after, so a run that died mid-flight is
  visible as `running` with no finish rather than as nothing at all.

Headers are set via `Response.OnStarting` because an error path may rewrite the response; the Problem
Details writer never calls `Response.Clear()`, which would discard `Retry-After` (ADR-0020).

## Adding telemetry

1. **Prefer an existing signal.** Before adding a metric, check whether the outbox meter, `job_runs`,
   the health checks or an existing span already answers the question.
2. **Name for the question it answers**, not for the code that emits it. `oldest pending age` beats
   `outbox_loop_iterations`.
3. **Low cardinality.** Never put an organization id, user id, device id, file key or free text into a
   metric dimension. Ids belong on spans and in log scopes.
4. **Spans wrap a unit of work with a boundary** — a handler, a job run, an external call — not every
   method.
5. **Do not add an exporter that fails closed.** A telemetry backend being down must never take the
   API down.

## Logging rules

- Log **ids**, not payloads and not personal data.
- **Never log** a token, refresh token, PIN, hash, device credential, activation code, API key,
  webhook secret or **signed storage URL**.
- Fault paths log the exception **type** and a redacted summary bounded in length — the outbox bounds
  errors to 500 characters and redacts before writing, and never logs the exception object.
- A refusal message must not teach: no differentiated POS refusals, no confirming an entity exists in
  another tenant.
- Levels: `Information` for a business fact worth reading later, `Warning` for a handled degradation
  (a job `skipped` is *not* a warning — it is the mechanism working), `Error` for something a person
  must act on.

## Verification and live diagnosis

1. Take the `X-Correlation-Id` or `X-Trace-Id` from the response or the Problem Details body.
2. Filter logs by that scope — every line of the request carries both.
3. If it crossed the outbox: `GET /api/v1/control/outbox/{messageId}` gives the message and every
   attempt at it; `GET /api/v1/control/outbox/health` gives backlog, oldest pending age, dead letters
   and throughput.
4. If it was a job: `GET /api/v1/control/jobs?job=…` gives the run log, including a `running` row with
   no finish.
5. If it was the Desktop client: its own rolling file log under the local profile. The live smoke
   should end with a clean application log; a clean log is part of the evidence.

## Desktop

`RollingFileLogger` writes the client's own log beside its local data. Binding failures do **not**
appear there by default — WPF writes them to the debugger's trace output. See `qrafig-desktop-wpf` for
how to surface them, and `qrafig-desktop-live-smoke` for the log's role as evidence.

## Do not

- Do not add high-cardinality metric dimensions.
- Do not log request or response bodies on a path that can carry credentials or PII.
- Do not register an exporter that blocks startup or shutdown.
- Do not trace `/health`.
- Do not treat a `skipped` job as an error.
- Do not remove the correlation scope to "reduce noise" — it is what makes a production report actionable.

## Related skills

`qrafig-outbox-jobs` · `qrafig-appsec` (redaction) · `qrafig-diagnostics` (triage procedure) ·
`qrafig-api-endpoints` (middleware order) · `qrafig-performance`.
External: ASP.NET Core OpenTelemetry configuration — see `docs/ai/sources.md`.
