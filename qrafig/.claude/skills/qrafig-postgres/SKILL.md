---
name: qrafig-postgres
description: PostgreSQL behaviour QRAFIG depends on — transaction isolation and the REPEATABLE READ snapshot used for shift reads, transaction-scoped advisory locks, SELECT FOR UPDATE and SKIP LOCKED claims, partial and unique indexes as invariants, deterministic lock ordering to avoid deadlocks, cursor-pagination index design, query plans and diagnosing a slow or deadlocking statement. Use for locking, isolation, index, deadlock and query-plan work against PostgreSQL 18.
when_to_use: Advisory locks, SKIP LOCKED, isolation levels, deadlocks, unique or partial index design, slow queries, EXPLAIN plans, cursor pagination indexes, PgBouncer and pooling questions.
---

# PostgreSQL in QRAFIG

Target: **PostgreSQL 18** (`compose.yaml`, and the integration suite's `postgres:18-alpine`).
Driver: Npgsql. Confirm versions in `compose.yaml` and `Directory.Packages.props`.

## Read first

- `compose.yaml` and `Directory.Packages.props` — the PostgreSQL and Npgsql versions actually in use.
- `backend/src/Qrafig.Application/Finance/FinanceLocks.cs` — the written-down lock order.
- `backend/src/Qrafig.Infrastructure/Services/PostgresJobLock.cs` — the advisory-lock job gate.
- `backend/src/Qrafig.Application/Common/Paging.cs` — cursor pagination.
- `docs/implementation-status.md` → `## Migration history` — every index and why it has its filter.
- ADRs 0016, 0018, 0019, 0037, 0094, 0097, 0102, 0108, 0128, 0136, 0194, 0196.

## Isolation

Default is **read committed**, and each statement sees a fresh snapshot. That is the cause of a real
QRAFIG defect class: a result assembled from several statements can contain two figures that are each
defensible and impossible together — a `saleCount` including a sale whose money is missing from
`cashSalesMinor`.

**A read that must be one moment runs over one `REPEATABLE READ` snapshot** (ADR-0136): no lock, so
the next customer never waits behind a report, and read-only, so it can never fail to serialize. This
is what a till's X report is built on. Use the same shape for any multi-statement read whose parts
must agree.

## Advisory locks

Transaction-scoped advisory locks (`pg_advisory_xact_lock`) are QRAFIG's serializer of choice where
two lawful writers must queue rather than conflict:

- **Per shift** — sale, cash in, cash out, void, return posting, approval, close and force-close all
  take it, so two requests can never both read "open" and both commit (ADR-0128).
- **Per account** — a balance is serialized by the account it belongs to (ADR-0194).
- **Per tenant** — storage capacity is reserved before the bytes, under a tenant lock (ADR-0097).
- **Per job** — one instance runs a job, decided by an advisory lock; the loser records `skipped`,
  which is the mechanism working rather than an error (ADR-0094). There is no table behind it, which
  is exactly why it was chosen.

**Lock order is global and written down.** Finance's is: the calling domain's scope (drawer, customer,
certificate), then the record being decided about, then one section per account **ascending by id**,
then the document-number gate — see `FinanceLocks.cs`. Inventory sorts every operation's lines by
`product_id` before touching anything (ADR-0037). Opposite operations then queue instead of
deadlocking. If you add a path that takes two locks, put it in the existing order.

Advisory locks are **session or transaction** scoped. Under a transaction-pooling proxy (PgBouncer in
transaction mode) a *session*-level advisory lock is unsafe; use the transaction-scoped form.

## Claiming work

```sql
UPDATE …
SET status = 'Processing', claimed_by = …, lease_expires_at = …
WHERE id IN (
    SELECT id FROM … WHERE status IN ('Pending','RetryScheduled') AND available_at <= now()
    ORDER BY available_at
    FOR UPDATE SKIP LOCKED
    LIMIT @batch
)
RETURNING …;
```

**One statement.** Workers take disjoint batches, so adding an instance adds throughput rather than
contention (ADR-0102). The claim's index is partial on the claimable statuses — without the filter it
grows with every event ever published and the claim scans history to find the few that are due.

A claim is a **lease**, and ownership is proved from the row — status, claimant, live lease — before
the message, before every handler and again before the commit. A worker that lost its lease stops
without writing anything (ADR-0108).

## Indexes as invariants

A partial unique index is how QRAFIG makes a rule true rather than intended. See
`qrafig-efcore-migrations` for the catalogue and the EF foreign-key interaction. Two rules:

1. A pre-check in code is an optimization; the index is the guarantee.
2. The loser of an index collision must be translated by **constraint name**, never by treating any
   `23505` as your expected collision (ADR-0129).

Index the minority state. Queues, claims, sweeps and "needs attention" reads are all partial:
`WHERE status = 'Reserved'`, `WHERE next_attempt_at IS NOT NULL`,
`WHERE status IN ('Failed','Running')`, `WHERE adjustment_entry_id IS NULL AND difference_minor <> 0`.

## Cursor pagination

Cursor (keyset) pagination for large mutable collections; offset only for small stable sets
(ADR-0016). A cursor-complete queue must be able to walk to the end — an operational queue capped like
history buries unresolved work (ADR-0200). Give the ordering columns their composite index **from the
start**: sales carry their query-path indexes from day one precisely so that adding them later is not
a migration on a table that has grown (ADR-0055, ADR-0075).

Cursors must be tenant-safe: a cursor minted in one organization must not be replayable in another.

## Deadlocks

Symptom: PostgreSQL kills one transaction with `40P01`, and neither operator did anything wrong.
Cause is almost always **two paths taking the same rows in different orders**.

1. Identify the two statements and the rows each takes, in order.
2. Find or define the canonical order (sort lines by `product_id`; sort accounts ascending by id).
3. Apply the order at the **lowest** shared point — `FinanceLedger.WithAccountsAsync` sorts the pair
   so a caller cannot get it wrong.
4. Prove it: fire the opposite operations simultaneously from independent clients and assert they
   queue rather than error.

Do not "fix" a deadlock by retrying blindly; that hides an ordering bug and doubles the work.

## Query plans and slowness

1. Reproduce with realistic data volume; a plan on ten rows says nothing.
2. `EXPLAIN (ANALYZE, BUFFERS)` the actual statement (capture the SQL EF generated).
3. Look for: sequential scan on a large table, a filter that could be an index predicate, a sort that
   an index could satisfy, a nested loop over many rows, and N+1 from the application side.
4. Change **one** thing, re-measure, and check you did not weaken an index another path depends on.
5. Record the before and after numbers.

## Pooling and capacity

Npgsql pooling is mandatory. At larger scale the contract is a bounded connection budget and PgBouncer
**transaction** pooling rather than one physical connection per active device
(`docs/api-roadmap.md` § Capacity and scaling contract). High-growth append-only tables — sales, sale
lines, movements, audit, sync feed, webhook inbox/outbox — get query-path indexes, retention rules and
measured partitioning before they become bottlenecks.

## Verification

Prove a locking or isolation change by **observation**, not by argument: fire genuinely simultaneous
requests from independent clients and assert the invariant (see `qrafig-concurrency`). Prove an index
with a plan before and after on realistic volume. Prove a claim statement the way the ledger proves
the outbox one — hold rows under `FOR UPDATE SKIP LOCKED` in one session while another runs the
production `UPDATE`, and confirm it comes away with only the rest. Prove a migration's index against
a **populated** database and confirm its filter with the definition PostgreSQL reports.

## Do not

- Do not rely on a `SELECT` to make a uniqueness decision.
- Do not take a session-scoped advisory lock on a pooled connection.
- Do not add a retry loop around a deadlock instead of fixing the order.
- Do not use `SERIALIZABLE` where an advisory lock expresses the intent better and does not abort.
- Do not add an index without knowing which query uses it, or remove one without checking who did.
- Do not pre-aggregate a report into a table; QRAFIG recomputes from documents (ADR-0071).

## Related skills

`qrafig-concurrency` · `qrafig-efcore-migrations` · `qrafig-outbox-jobs` · `qrafig-performance` ·
`qrafig-reporting`. External Postgres skills: `docs/ai/sources.md`.
