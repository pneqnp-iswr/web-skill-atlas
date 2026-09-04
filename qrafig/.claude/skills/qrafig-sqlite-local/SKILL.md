---
name: qrafig-sqlite-local
description: Work on QRAFIG's local SQLite databases on the till and in QRAFIG Desktop — the numbered append-only user_version migration chain, WAL and the per-connection PRAGMAs, BEGIN IMMEDIATE for allocate-and-write, durability before reporting success, refusing a newer schema rather than downgrading, per-device keys, and the projection-not-a-domain rule. Use for any change to the local database, the operation queue, the POS journal or a local cache or projection.
when_to_use: Local database schema or migration, operation queue, POS journal, local projections and caches, SQLite locking or durability, "PRAGMA user_version", offline storage questions.
---

# Local SQLite in QRAFIG

Two local databases exist: `desktop/src/Qrafig.Desktop.Infrastructure/Persistence/LocalDatabase.cs`
(QRAFIG Desktop) and `apps/pos-windows/Qrafig.Pos.Core/PosDatabase.cs` (the POS core). Both use
`Microsoft.Data.Sqlite.Core` with `SQLitePCLRaw.bundle_e_sqlite3`.

**Do not replace `Microsoft.Data.Sqlite.Core` with `Microsoft.Data.Sqlite`** — that package may
restore an older native SQLite bundle. The native runtime is initialized once by
`SQLitePCL.Batteries_V2.Init()` behind a `Lazy<bool>`; without it every call fails with a missing
entry point.

## Read first

- `desktop/src/Qrafig.Desktop.Infrastructure/Persistence/LocalDatabase.cs` — the connection settings
  and the whole `user_version` migration chain, with `LocalMigrations.All`.
- `desktop/src/Qrafig.Desktop.Infrastructure/Persistence/SqliteOperationQueue.cs`, `SqlitePosJournal.cs`.
- `apps/pos-windows/Qrafig.Pos.Core/PosDatabase.cs`.
- `README.md` § *SQLite runtime*; `docs/implementation-status.md` for the current schema version.
- ADRs 0113, 0116, 0142, 0149, 0185, 0203, 0207.

## It is a projection, not a second domain

Nothing in the local database derives a balance, enforces a business invariant or holds a document the
server does not already hold. It **caches what a till needs to keep working with no internet** and
**queues what the till captured**. A client that reimplemented the domain would be a second authority
for the same rules, running on the machine nobody administers.

Corollary: when a module is online-only by decision (Warehouse mutations, Transfers, Customers
Backoffice, Finance, Employees), there is **no local table and no queue** — deliberately, so there is
nowhere for a change to wait (ADR-0142, ADR-0149, ADR-0185, ADR-0203, ADR-0207). Do not add one to
"improve" the experience.

## The migration chain

- Migration is by **`PRAGMA user_version`** — numbered, append-only, and **never edited once
  released**. A released migration that changes is a machine whose schema depends on when it last
  updated.
- Each step runs in **one transaction with its own version bump**, so a migration that fails half way
  leaves the version where it was and is retried whole.
- `CurrentSchemaVersion` is raised by one per migration. Read the current value from the source and
  the ledger, not from memory.
- A file at a version **ahead** of this build is **refused, never downgraded** — an installation
  rolled back to an older client must not have its schema quietly rewritten by code that does not
  know what the newer one added.
- Every caller opens through `LocalDatabase.OpenAsync`, so there is no path to an unmigrated database.

A migration that changes a uniqueness rule must move the index too. Local migration 3 made the
operation sequence per-device and left the column-level `UNIQUE` from migration 1 in place, so a
replacement till's first sale would have failed at the `INSERT`; migration 4 rebuilt the table with
the constraint on `(device_id, device_sequence)`.

## Connection settings

```
PRAGMA journal_mode = WAL;      -- set at migration time; survives the connection
PRAGMA foreign_keys = ON;       -- per connection
PRAGMA busy_timeout = 5000;     -- per connection
```

`foreign_keys` and `busy_timeout` are **per connection**: setting them once at creation leaves every
later connection on the defaults. Shared cache is deliberately **not** used — it serialises every
connection in the process onto one lock, which is the stall a till cannot afford while a sync pass is
writing. WAL gives concurrent readers instead.

## `BEGIN IMMEDIATE` for allocate-and-write

Use `IsolationLevel.Serializable` on `BeginTransactionAsync`, which maps to `BEGIN IMMEDIATE`: the
transaction takes its write lock now rather than on the first write, so two threads capturing at once
cannot both read the same next sequence and then have one fail at commit.

Allocate the sequence and write the row **in the same transaction**. Two statements would let a crash
consume a sequence number no operation ever used — and since the server reports the lowest sequence it
has never received, a gap that is not a real operation looks forever like a device still holding
something.

## Durability before success

The load-bearing ordering of an offline till:

> **the operation is on the disk before the cashier is told it succeeded.**

`EnqueueAsync` does not return until the commit has happened; everything after the commit line is a
fact about a disk. A sale that exists in a view model and not on disk is a sale the next power cut
deletes.

The sale and its receipt commit **together**, in one transaction and through one writer
(`IPosJournal.CommitSaleAsync` — open, `BEGIN IMMEDIATE`, **re-read the open shift inside the
transaction**, write the sync operation via the same writer the ordinary enqueue path uses, write the
receipt projection, commit). Do not add a second copy of the operation insert; that is exactly how the
migration-4 defect arose. Synchronization is attempted **after** success is reported and its result is
advisory (ADR-0116).

## Per-device keys

Queue, sequence and cursor rows carry `device_id`. Without it a replacement till pushes its
predecessor's work under its own credential. Stranded work is **surfaced and never deleted**
(ADR-0113). One open shift per device is enforced by a **partial unique index**, as the server
enforces its own.

## Failure modes

- Setting `foreign_keys` or `busy_timeout` once and assuming later connections inherit them.
- `BEGIN DEFERRED` for a read-then-write, then a commit-time conflict.
- Reporting success to the cashier before the commit returns.
- Editing a released local migration instead of adding the next one.
- Downgrading a newer schema instead of refusing it.
- A second insert path for the same row, so a later constraint change misses one of them.
- Trusting a shift id from a view model instead of re-reading it inside the transaction.
- Adding a local table for a module that is online-only by decision.
- Holding a long read transaction on the UI thread while a sync pass writes.

## Verification

`desktop/tests/Qrafig.Desktop.Tests` — `LocalDatabaseTests`, `LocalMigrationTests`,
`PosCheckoutDurabilityTests`, `OfflineColdStartTests`, `SyncCoordinatorTests`. `SqliteCollection`
serializes tests sharing a file. For a schema change, prove: a fresh file reaches the new version; an
existing file at the previous version migrates; a file at a **higher** version is refused; and the
new invariant is enforced by the index rather than by the calling code.

For a durability change, prove it by **killing the process** between capture and sync and restarting —
`OfflineColdStartTests` and the POS durability tests are the pattern. On Windows, also confirm
`PRAGMA user_version` on the real file after a live run.

## Do not

- Do not replace `Microsoft.Data.Sqlite.Core` with `Microsoft.Data.Sqlite`.
- Do not assume `foreign_keys` or `busy_timeout` are inherited by a new connection.
- Do not use `BEGIN DEFERRED` for a read-then-write.
- Do not report success before the commit returns.
- Do not edit a released local migration, or downgrade a newer schema.
- Do not add a second insert path for a row that a constraint change would have to follow.
- Do not trust a shift id from a view model instead of re-reading it in the transaction.
- Do not add a local table or queue to a module that is online-only by decision.

## Related skills

`qrafig-offline-sync` · `qrafig-pos-domain` · `qrafig-desktop-workspace` · `qrafig-testing` ·
`qrafig-concurrency`.
