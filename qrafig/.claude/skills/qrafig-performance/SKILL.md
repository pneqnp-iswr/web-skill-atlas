---
name: qrafig-performance
description: Measure and improve QRAFIG's performance honestly — API and EF query cost, PostgreSQL plans and index design, report bounds, Desktop startup and WPF rendering and virtualization, local SQLite and sync batch size, memory and payload size — with a measurement before and after rather than a claim. Use for any "make this faster" request, a slow report or list, a sluggish screen, or capacity work.
when_to_use: Slow endpoint, slow query, slow report, slow list or screen, high memory, large payloads, Desktop startup time, sync batch tuning, capacity planning.
---

# Performance work in QRAFIG

## Read first

- The endpoint, query or view you are asked to make faster, and the test that covers it.
- `docs/api-roadmap.md` § *Capacity and scaling contract* — the measured targets and the pooling rules.
- `backend/src/Qrafig.Api/Observability/ObservabilitySetup.cs` — what is already instrumented.
- ADRs 0016, 0055, 0071, 0074, 0075, 0110, 0136.

## The discipline

1. **Reproduce with realistic volume.** A plan over ten rows says nothing. A grid that is fast with
   twenty products says nothing about twenty thousand.
2. **Measure before.** Record the number.
3. **Find the cause**, not a plausible cause. A guess that happens to help is still a guess.
4. **Change one thing.**
5. **Measure after**, the same way.
6. **Check what else you moved** — an index that helps one query can be the index another path was
   using, and removing a column from a projection can break a client that mirrors the contract.
7. **Report both numbers.** A performance claim without a measurement is not a result.

## Where the cost usually is

| Layer | Look for | Tools |
| --- | --- | --- |
| **EF Core** | N+1 over navigations in a list endpoint; tracking on a read-only query (`AsNoTracking`); a projection that pulls whole entities to use two fields; a client-side evaluation | capture the generated SQL; count the round trips |
| **PostgreSQL** | sequential scan on a large table; a filter that should be an index predicate; a sort an index could satisfy; a missing composite index for a cursor's ordering | `EXPLAIN (ANALYZE, BUFFERS)` on the real statement |
| **API** | an unbounded read; a synchronous report over a wide window; a response carrying fields nobody reads; missing `no-store` or wrong caching | the endpoint's own timings, plus the OTel spans |
| **Outbox / jobs** | a claim without its partial index scanning history; a batch size that makes the lease expire mid-batch | `Qrafig.Outbox` meter: backlog, oldest pending age, throughput |
| **Desktop startup** | work on the UI thread before the first frame; a `.Result` in a startup path; loading a projection eagerly that a screen would load anyway | the rolling file log's timestamps |
| **WPF rendering** | a virtualizing list inside a `StackPanel` or unbounded `ScrollViewer`, which measures every item; a converter doing work per row; a binding that re-evaluates a collection; too many `DynamicResource` lookups in an item template | the live run, at realistic row counts |
| **Local SQLite** | a long read transaction blocking a sync write; shared cache serialising connections; a query without its index; a busy timeout being hit | the client log; the queue depth |
| **Sync** | batch size versus a shop's real backlog; a projection rebuilt whole when it could be incremental | the sync diagnostics service |

## QRAFIG-specific constraints on the fix

- **Do not pre-aggregate a report.** A report recomputes from documents; nothing is materialized
  (ADR-0071). The reporting phase deliberately added **indexes only**. If a report is slow, the answer
  is an index, a bound, or a narrower window — not a rollup table.
- **A synchronous report is bounded and says what to do about it** (ADR-0074). Counting before loading
  and refusing is the designed behaviour, not a limitation to remove.
- **Sales carry their query-path indexes from the start** (ADR-0055, ADR-0075) precisely so that adding
  one later is not a migration on a table that has grown. Give a new high-volume table its index in the
  same migration.
- **Cursor pagination**, not offset, for large mutable collections (ADR-0016). Do not "optimize" a
  cursor into an offset.
- **A shift read is one `REPEATABLE READ` snapshot** — read-only and lock-free, so a report never makes
  the next customer wait (ADR-0136). Do not convert it into a lock to make it simpler.
- **Npgsql pooling is mandatory**; at scale the contract is a bounded connection budget and PgBouncer
  **transaction** pooling rather than one connection per active device. A *session*-scoped advisory
  lock is unsafe under transaction pooling — use the transaction-scoped form.
- **The capacity target** in `docs/api-roadmap.md` is ~10 000 active store customers including ≥2 000
  concurrent POS devices and a ~400 RPS mixed baseline, validated by p95/p99 latency, database I/O,
  connection use, queue lag and restore performance — not by tenant count.
- **Do not weaken a correctness property for speed**: not the currency separation, not the tenant
  scoping, not `checked` money arithmetic, not the lock order, not a partial unique index.

## Desktop specifics

- The design system uses `DynamicResource` everywhere so the theme can swap live. That is a deliberate
  cost. Do not convert them to `StaticResource` for speed — you break theming.
- `DataGrid` virtualization is one of the reasons WPF was chosen. Preserve it: no virtualizing list
  inside a `StackPanel`, no `Height="Auto"` on a scrolling region that removes the viewport.
- Startup: device identity loads **first** and asynchronously, with no `.Result` (ADR-0110). Do not
  move work ahead of it or block on it.

## Verification

The before and after numbers, on the same data shape; the affected test suites still green; a plan
comparison for a query change; and — for a Desktop change — the live run at realistic row counts.
State the measurement method. If you could not measure, say the change is unverified.

## Do not

- Do not claim a speedup you did not measure.
- Do not add an index without knowing the query, or drop one without checking who used it.
- Do not add a cache without an invalidation story and a tenant-scoped key.
- Do not pre-aggregate, materialize or denormalize a figure that is derived by decision.
- Do not raise a bound or a batch size to make a symptom go away.
- Do not trade a correctness property for latency.

## Related skills

`qrafig-postgres` · `qrafig-efcore-migrations` · `qrafig-reporting` · `qrafig-desktop-wpf` ·
`qrafig-sqlite-local` · `qrafig-observability` · `qrafig-outbox-jobs`.
External: .NET performance analysis and trace collection, EF Core query optimization — `docs/ai/sources.md`.
