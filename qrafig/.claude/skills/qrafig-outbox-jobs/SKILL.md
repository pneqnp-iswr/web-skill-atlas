---
name: qrafig-outbox-jobs
description: Work on QRAFIG's post-commit machinery — the transactional outbox (versioned payloads, single-statement SKIP LOCKED claiming, leases proved from the row, deterministic jittered retry, explicit retryable-versus-permanent classification, dead letters, one committed success per handler) and the advisory-locked scheduled jobs with their job_runs records. Use when adding an integration event, an outbox handler, a webhook, a notification or a scheduled job, or when the backlog, retries or dead letters misbehave.
when_to_use: Integration events, outbox handlers, webhooks, notifications, scheduled jobs, backlog or dead-letter investigation, "at-least-once", retry and recovery behaviour.
---

# Outbox and background jobs

## Read first

- `README.md` § *Transactional outbox* and § *Background jobs* — the operational contract.
- `backend/src/Qrafig.Api/Outbox/OutboxWorker.cs`, `backend/src/Qrafig.Api/Jobs/JobScheduler.cs`,
  `backend/src/Qrafig.Application/Outbox/*`, `backend/src/Qrafig.Application/Jobs/*`,
  `backend/src/Qrafig.Infrastructure/Services/PostgresJobLock.cs`.
- Tests: `OutboxTests`, `OutboxTestHandler`, `JobTests`, `NotificationTests`.
- ADRs 0015, 0089, 0094, 0095, 0096, 0102, 0103, 0104, 0105, 0106, 0107, 0108, 0078, 0081, 0082.

## The outbox contract

An integration event is written **in the same transaction as the change it describes**, so a sale and
the fact that somebody should be told about it commit together or neither does. Nothing is sent
inline: an outbound call inside a sale's transaction holds a database lock for as long as somebody
else's server takes to answer.

| Concern | Behaviour |
| --- | --- |
| Delivery | A **hosted worker**, not the 30-second scheduler — half a minute of latency on "a sale happened" is half a minute where a shop's e-commerce stock is wrong. Polls with a half-second floor, backs off to five seconds when idle, returns immediately after a full batch. |
| Payload | An explicit **versioned contract**, never a serialized entity (ADR-0103). No tokens, signed URLs, credentials, file contents or unneeded PII. |
| Claiming | One `UPDATE … FOR UPDATE SKIP LOCKED` statement. Every replica runs the worker; workers take disjoint batches, so adding an instance adds throughput rather than contention (ADR-0102). |
| Retry | Exponential from 5s, capped at 10 minutes, with **deterministic** jitter derived from the message id — the same message always backs off to the same instant (ADR-0104). |
| Classification | **Explicit.** A 4xx (except 409/429), an unreadable payload or `OutboxPermanentException` dead-letters immediately; anything unrecognised is treated as retryable. |
| Attempts | Six, then dead-lettered. Dead letters are kept, never deleted. |
| Idempotency | One **committed** success row per `(message, handler)`, enforced by a partial unique index (ADR-0105). |
| Crash recovery | A claim is a lease; `outbox.recovery` returns messages whose worker stopped answering, every minute (ADR-0106). |
| Claim ownership | Proved from the row — status, claimant, live lease — before the message, before every handler and again before the commit. A worker that lost its lease stops without writing anything (ADR-0108). |
| Errors | Bounded to 500 characters and redacted before writing. Fault logs carry the message id, worker id, exception **type** and the redacted summary — never the exception object. |

## What it promises, and what it does not

- Queue delivery is **at-least-once**. A worker can perform an effect and then fail to commit, and the
  message will be claimed again.
- The database permits only **one committed successful delivery record per `(message, handler)`** —
  that is a statement about **rows**, not about the outside world. **A handler whose effect lands
  elsewhere must be independently idempotent.** The shipped webhook fan-out satisfies this by
  construction: it passes the outbox message id as the webhook event id, so a repeat asks to queue a
  pair the existing unique index already refuses.
- **Per-aggregate ordering is not guaranteed in this version.** The claim orders globally and workers
  take disjoint batches, so two events about one product can be in flight at once and arrive in either
  order. Consumers must order by **event id, `occurredAt` and the contract's own data**, never by
  arrival.

When you add a handler, state in its own words how it is idempotent against the **external** system.
"The index stops a second row" is not an answer to "the e-commerce site got two stock updates".

## Scheduled jobs

Scheduled work — the notification scan, billing transitions, webhook dispatch, the three storage
passes, outbox recovery — runs on a loop **inside the API**. **Every replica runs the same loop**; a
PostgreSQL advisory lock decides which one does the work, so there is no leader election and no
instance configured as special. A job whose lock is held records **`skipped`**, which is the mechanism
working rather than an error (ADR-0094).

Every execution writes a `job_runs` row, written **before** the work and completed after — so a run
that died mid-flight is visible as `running` with no finish rather than as nothing at all (ADR-0095).

**A scheduled job calls the same service its tenant-facing endpoint calls** (ADR-0096), so a hand-run
and a timer-run cannot drift. If you add a job, add or reuse the endpoint; do not write a second
implementation.

Control surfaces (operator role, audited):

```
GET  /api/v1/control/jobs?job=notifications.scan&organizationId=<id>
POST /api/v1/control/jobs/{job}/run[?organizationId=<id>]
GET  /api/v1/control/outbox/health
GET  /api/v1/control/outbox?status=dead_lettered
GET  /api/v1/control/outbox/{messageId}
POST /api/v1/control/outbox/{messageId}/replay   # dead letters only
POST /api/v1/control/outbox/{messageId}/cancel   # pending or retry-scheduled; reason required
POST /api/v1/control/outbox/recover
```

Control can **look, replay and cancel, and nothing else** (ADR-0107).

## Notifications specifically

The audience is **derived from the permission each kind names**, never declared; a preference can
narrow it, never widen it. Deduplication is by an **occurrence key the caller states**, enforced by a
unique index, and is **per recipient**. The rendered text is **stored**, so correcting a template does
not rewrite what somebody was told. A channel that is off is recorded as **suppressed**, never
silently dropped (ADR-0077 – ADR-0081).

Conditions that time makes true are found by a pass somebody invokes, not by a timer inside the
application — a timer fires on every replica at once (ADR-0081).

## Verification — adding an event or handler

1. Write the event **in the same transaction** as the change.
2. Define a **versioned payload contract**; no entity, no secret, no signed URL, minimal PII.
3. Give the message a dedup key where enqueueing can legitimately repeat (an offline till replaying its
   day must raise one event per sale).
4. Make the handler idempotent **against the external effect**, and say how.
5. Classify failures explicitly; do not let an unrecognised failure dead-letter.
6. Add metrics and a log line that carries ids, not payloads.
7. Test: delivery, duplicate claim, lease loss, retry schedule determinism, permanent-failure
   dead-letter, and recovery after a simulated crash. Tests drive the dispatcher directly — the worker
   is disabled in the suite.

## Do not

- Do not send anything inline inside a domain transaction.
- Do not serialize an entity as a payload.
- Do not rely on arrival order.
- Do not treat the unique index as proof of external exactly-once.
- Do not delete dead letters.
- Do not add a timer inside the application for tenant-wide work.
- Do not implement a job's logic separately from the endpoint that exposes it.
- Do not log the exception object on a fault path.

## Related skills

`qrafig-postgres` (SKIP LOCKED, advisory locks, partial indexes) · `qrafig-concurrency` ·
`qrafig-observability` · `qrafig-appsec` (payload redaction) · `qrafig-storage` (the three passes).
External: idempotency and webhook-handler patterns — see `docs/ai/sources.md`.
