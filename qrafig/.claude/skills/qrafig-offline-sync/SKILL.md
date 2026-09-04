---
name: qrafig-offline-sync
description: QRAFIG's offline-first synchronization — the operation as the unit of idempotency, the four settled outcomes and the one that leaves no row, duplicate pushes settling as applied and duplicate rather than 500, the change feed ordered by transaction id, per-device queues and cursors, reconciliation written beside the local record rather than over it, crash and reconnect behaviour, and which modules deliberately have nowhere to wait. Use for any sync, offline capture, replay, change-feed, projection or reconnect work.
when_to_use: Offline capture and replay, sync push or pull, change feed and cursors, duplicate operations, crash and restart, reconnect, device replacement, stranded work, "fix offline sync".
---

# Offline sync in QRAFIG

QRAFIG is **server-authoritative and operation-log based**. It is not a CRDT system and there is no
last-write-wins merge. Generic "offline-first sync" advice built on CRDTs or automatic conflict
resolution **contradicts this architecture** — do not import it.

## The unit of idempotency is the operation, not the request (ADR-0047)

The transport-level `Idempotency-Key` covers one HTTP request and survives a lost response, nothing
more. It does not survive a client restart, a re-queue, or a replay from different hardware.

`operationId` is generated **on the device, when the operation happens** — not when it is transmitted —
and is unique per device, enforced by an index rather than by an application check two concurrent
pushes could both pass:

```
ux_sync_operations_device_operation  UNIQUE (device_id, operation_id)
```

| Outcome | Stored | The device should |
| --- | --- | --- |
| `applied` | yes, with the handler's result | move on |
| `duplicate` | already was | move on; the original result is replayed **verbatim** |
| `rejected` | yes, with the failure | move on — it will not read differently next time |
| `needs_attention` | yes, unhandled | stop retrying; a human or a deployment resolves it |
| *(transient)* | **no row** | retry — nothing was recorded |

**A transient failure deliberately leaves no row.** The handler's work and the record of that work
commit in one transaction, so a failure rolls back both.

## Two pushes of one operation settle as applied and duplicate, not as 500 (ADR-0129)

The "have I seen this?" read cannot see an uncommitted transaction, so two simultaneous first-time
pushes both answer no and both run the handler. The unique index does its job. **Translate that one
constraint by name**:

```csharp
catch (Exception ex) when (db.IsUniqueViolation(ex, "ux_sync_operations_device_operation"))
```

The loser re-reads the committed row and answers the way a duplicate is always answered: the winner's
stored result verbatim, or `OPERATION_PAYLOAD_MISMATCH` if the bodies disagree. If nothing is there
after all, the exception travels on — whatever collided is not this case.

The fix exposed a second contention: `DeviceSyncState` carries a concurrency token, so two overlapping
pushes from one till collide on the row tracking how far it has got, **after** both operations
committed. That state is derived, so the push **re-reads and re-applies this batch's outcomes**,
bounded to four attempts, each starting from the freshly read row.

A till told "500" retries something that already worked and never learns the result it needs to
reconcile against. That is why this matters.

## The change feed is ordered by transaction id (ADR-0048)

A `bigserial` cursor is silently, intermittently wrong: ids are assigned at **insert** and rows become
visible at **commit**, and those orders differ. An entry can end up permanently beneath a device's
cursor — for a POS that means a price change no till ever sees.

```sql
WHERE commit_id < pg_snapshot_xmin(pg_current_snapshot())
ORDER BY commit_id, id
```

`commit_id` is `pg_current_xact_id()` taken as the row's column **default**, so the value comes from
the transaction actually doing the insert. The watermark is read in its own statement first; a
slightly stale watermark only **withholds** rows, never skips them.

The change feed maintains the **POS projection**, not only the browse cache (ADR-0119). A projection
that cannot consume a deletion **says so and is repaired** (ADR-0122). The return-reason catalog rides
the feed; retirement is a flag, not a deletion (ADR-0130).

## Reconciliation is written beside, never over (ADR-0118)

An `IOperationResultReconciler`, dispatched by operation type, with three rules:

- **Additive.** Every column is `COALESCE($new, existing)`; no locally captured value appears in any
  `UPDATE`. A server total differing from the printed one produces **two recorded figures, not a
  correction** — the receipt in the customer's hand is the evidence, and which is right is a question
  for a person.
- **Idempotent.** A `duplicate` replays the original result, so applying it twice must be
  indistinguishable from applying it once.
- **Success only.** Called for `applied` and `duplicate` and nothing else. Stamping server identifiers
  onto a rejection would make a refusal read as done.

## Per-device everything (ADR-0113)

Queue rows, the sequence counter and the cursor all carry `device_id`. Without it a replacement till
pushes its predecessor's work under its own credential. **Stranded work is surfaced and never
deleted.** Local sync state names the device that created it.

Offline operations **reference each other by operation id** (ADR-0054) — a shift opened during an
outage has no server id, so the operation that opened it is its name.

**An offline operation may name its own cashier, within limits** (ADR-0056), and a synchronized
operation is attributed to the person who rang it even if they have since been suspended
(ADR-0126). Do not "harden" this.

## Where offline stops

Not everything waits. These are **online only, with nowhere for work to wait** — by decision, and the
absence of a local table is the mechanism:

| Area | Decision |
| --- | --- |
| Warehouse mutations | read-only offline with a dated last-known board (ADR-0142) |
| Transfers | an instruction about shared stock; none of it captured offline (ADR-0149) |
| Customers Backoffice | online only, no cache, no queue (ADR-0185) |
| Finance | online only, no local table, no queue (ADR-0203) |
| Employees Backoffice | online only (ADR-0207) |

Do not add a queue to one of these to "improve" it. Something has to ask whether the server is back
(ADR-0204) — that is the reconnect probe, not a mutation queue.

## Freshness and version floors

Offline sign-in material is **re-read whole**, and refreshing it is **not** authority (ADR-0131). A
version floor is compared **numerically** and **withholds new work only** (ADR-0117). Unknown is a
value, and it never grants anything (ADR-0115) — `AllowsNewWork` is `bool?`, connectivity has one
author, and a failed projection of a claimed type keeps the cursor.

## Read first

- `backend/src/Qrafig.Application/Sync/` — `SyncPushService`, `SyncOperationHandler`,
  `ChangeFeedService`, `ChangeFeedCursors`, `PayloadCanonicalizer`, `SyncDiagnosticsService`.
- `desktop/src/Qrafig.Desktop.Infrastructure/Persistence/SqliteOperationQueue.cs`,
  `SqlitePosJournal.cs`; `desktop/src/Qrafig.Desktop.Infrastructure/Sync/` — `DeviceSyncChannel`,
  `PosProjections`.
- Tests: `SyncTests`, `OfflineSalesTests`, `PosFreshnessTests` (backend);
  `SyncCoordinatorTests`, `PosSaleSyncTests`, `PosReconciliationTests`, `PosProjectionTests`,
  `PosLegacyProjectionTests`, `OfflineColdStartTests`, `ReconnectProbeTests` (Desktop).
- ADRs 0009, 0011, 0047, 0048, 0054, 0056, 0112 – 0122, 0129 – 0131, 0142, 0149, 0204.

## Verification

Prove all of: disconnected capture; retry; a **duplicate push settling as `duplicate`, not `500`**; a
crash and restart with the operation still queued; reconnect; reconciliation written **beside** the
local values; and a rejection **not** stamped with server identifiers. Add a change-feed test that a
row committed late is still returned. For a projection change, prove a deletion is consumed or
explicitly reported and repaired.

## Do not

- Do not make a `SELECT` the idempotency guarantee.
- Do not catch every `DbUpdateException` as "already exists".
- Do not overwrite a locally captured figure with the server's.
- Do not reconcile a rejection.
- Do not order the change feed by an insert-time sequence.
- Do not drop stranded work.
- Do not refuse a late or after-the-fact operation for authority reasons.
- Do not import CRDT or last-write-wins merge semantics.
- Do not add a local queue to a module that is online-only by decision.

## Related skills

`qrafig-sqlite-local` · `qrafig-pos-domain` · `qrafig-authorization` · `qrafig-concurrency` ·
`qrafig-postgres` · `qrafig-desktop-workspace` · `qrafig-diagnostics`.
