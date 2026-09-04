---
name: qrafig-concurrency
description: Find and fix concurrency defects in QRAFIG — last-write-wins saves, check-then-insert races on unique indexes, approval and deletion races, counter and sequence claims, balance contention, plan-cap races, shift-close races, deadlocks from inconsistent lock order, and lost HTTP responses — and prove the fix with a real overlapping-request test. Use for any read-modify-write path, any "find race conditions" request, and any code that claims something no other caller may also claim.
when_to_use: Any read-modify-write, counter, uniqueness rule, status transition, approval, balance mutation or deletion; requests to audit for race conditions; unexplained 500s or 409s under load.
---

# Concurrency in QRAFIG

QRAFIG is a multi-user business system. "It works with one request" is not a result. For every
read-modify-write, answer out loud:

> **What happens if two legitimate clients do this at the same instant?**

Legitimate is the operative word. Two managers recording money against one account are both doing
something lawful; answering one of them with a conflict they did nothing to cause is a defect, not
safety (ADR-0194).

## The race catalogue — check each against your change

| Race | Shape | QRAFIG's answer |
| --- | --- | --- |
| **Last write wins** | two clients load a card, both save, the second silently discards the first | every save names the `rowVersion` it was composed against → `409 CONCURRENCY_CONFLICT` (ADR-0008, ADR-0164, ADR-0170, ADR-0197, ADR-0205) |
| **Check then insert** | `SELECT` finds nothing, both insert, one gets an unhandled unique violation → `500` | claim the code **inside the section that inserts it**; translate the named constraint (ADR-0171, ADR-0197, ADR-0129) |
| **Approval race** | two approvers both post one expense | serialize by the record being decided about (ADR-0198) |
| **Delete vs assign** | a role is deleted while an assignment commits in the gap, and a cascade takes it silently | both sides must contend on the **same key** — keying one side by code and the other by id means they never meet |
| **Sequence / document number** | two callers both take number N | claim under a lock, one statement (ADR-0053, ADR-0148, ADR-0160) |
| **Balance** | two postings both read the old balance | serialize by the account; take accounts in a fixed global order (ADR-0194, ADR-0196) |
| **Plan cap** | ceiling checked before the insert, so simultaneous hires all find room | check **inside** the gate that grants it (ADR-0206, ADR-0085) |
| **Shift close** | two requests both read "open" and both commit | a transaction-scoped advisory lock every participant takes (ADR-0128) |
| **Duplicate execution** | the same operation pushed twice | settle as `applied` + `duplicate`, never `500` (ADR-0129, ADR-0047) |
| **Lost answer** | the client never learns the outcome | one stable idempotency key per **intent**, not per attempt (ADR-0141, ADR-0148, ADR-0155, ADR-0162) |
| **Deadlock** | two operations take overlapping rows in opposite orders | sort lines/accounts into one deterministic order everywhere (ADR-0037, ADR-0196) |
| **Stale editor** | a form composed ten minutes ago | the save names its version; the server refuses rather than merging |
| **Snapshot tearing** | a report assembled from six statements at read-committed | one `REPEATABLE READ` snapshot for the whole read (ADR-0136) |

## Read first

- `backend/src/Qrafig.Application/Finance/FinanceLocks.cs` — the module's lock order, written down
  because it is a property of the module rather than of any method.
- `backend/src/Qrafig.Application/Sales/ShiftService.cs` — advisory-locked shift participation.
- `backend/src/Qrafig.Application/Sync/SyncPushService.cs` — duplicate-as-success.
- The existing race tests: `FinanceConcurrencyTests`, `InventoryConcurrencyTests`,
  `PurchasingConcurrencyTests`, `CustomerConcurrencyTests`, `EmployeeConcurrencyTests`,
  `OfflineSalesTests`. They are the specification.
- ADRs: 0008, 0037, 0102, 0128, 0129, 0136, 0141, 0148, 0173, 0194, 0196, 0198, 0206.

## Choosing the mechanism

| Situation | Mechanism |
| --- | --- |
| Two writers may lawfully contend and both should succeed in some order | **Transaction-scoped advisory lock** on the subject (account, shift, customer, certificate). Queue, do not conflict. |
| Two writers are editing the same record and only one should win | **`row_version` optimistic concurrency** → `409` |
| Uniqueness must hold no matter what | **Unique or partial unique index**, plus a named-constraint translation for the loser |
| Work must be taken by exactly one worker | `UPDATE … FOR UPDATE SKIP LOCKED` in **one** statement (ADR-0102) |
| One instance out of many should run a job | PostgreSQL **advisory lock**; the loser records `skipped`, which is the mechanism working (ADR-0094) |
| A client may retry an uncertain command | **Idempotency key on the intent** + the stored original response |

The guarantee lives in the **database**, never in the pre-check. A read cannot see an uncommitted
transaction, so "have I seen this?" answered by a `SELECT` is advisory only — it makes the common case
cheap and must never be the thing correctness rests on.

## Lock order

Deadlock is prevented by a **single global order**, not by cleverness. Finance's is written down: the
calling domain's scope first (drawer, customer, certificate), then the record being decided about,
then one section per account **ascending by id**, then the document-number gate. Nothing takes a
Finance scope and then reaches back for a shift. Inventory's is: sort every operation's lines by
`product_id` before touching anything, so all callers acquire rows in the same sequence.

If you add a path that takes two locks, put it in the existing order or extend the order deliberately
and record it.

## Writing the proof

A concurrency test that does not actually overlap is worse than none. The QRAFIG pattern:

```csharp
// Independent HttpClient instances: separate connections, separate scopes,
// separate DbContext instances. Two awaited calls on ONE client serialize
// in the client and prove nothing.
private HttpClient SecondClient(Shop shop)
{
    var client = factory.CreateClient();
    var auth = shop.Client.DefaultRequestHeaders.Authorization!;
    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue(auth.Scheme, auth.Parameter);
    return client;
}

var clients  = Clients(shop, 6);
var attempts = clients.Select(c => c.PostJsonAsync(route, body));   // released together
var results  = await Task.WhenAll(attempts);
```

Then assert the **invariant**, not the status codes: exactly one row exists; the ledger still sums to
the balance; nothing oversold; no `500` anywhere; both callers received an answer they can act on.

Write the test as a **reproduction first** — it must fail against the current implementation. A race
test that passes before the fix is testing something else.

## Failure modes

- Asserting `200 + 409` when the real invariant is "exactly one row". Status codes are the mechanism;
  the invariant is the contract.
- Catching every `DbUpdateException` as "already exists" instead of matching the constraint by name.
- Using an idempotency key per **attempt** — a retry then composes a new key and executes twice.
- Fixing a `500` by widening a catch, leaving the underlying double-execution in place.
- Serializing everything under one global lock; that turns a race into a queue for the whole tenant.
- Adding `Thread.Sleep` or ordering hacks to a test to make a race reproduce. Fire genuinely
  simultaneous requests instead.
- Treating a `409` on a derived row (a sync cursor, a projection) as the caller's problem when the
  work already committed — re-read and re-apply instead (ADR-0129).

## Verification

Backend integration suite; the new race test failing before the fix and passing after; no new `500`
under contention; and — where the path is a POS or Desktop one — the corresponding client behaviour
under a lost answer.

## Do not

- Do not make a pre-check the guarantee; the index or the lock is.
- Do not catch every `DbUpdateException` as your expected collision — match the constraint by name.
- Do not key an idempotency token to an attempt instead of an intent.
- Do not widen a `catch` to make a `500` disappear.
- Do not serialize a whole tenant under one lock to fix one race.
- Do not use `Thread.Sleep` or ordering tricks to make a race reproduce.
- Do not answer a caller `409` on a derived row after their work already committed — re-read and re-apply.
- Do not assert status codes where the invariant is "exactly one row".

## Related skills

`qrafig-postgres` (locks, isolation, indexes) · `qrafig-testing` (harness) · `qrafig-money-finance` ·
`qrafig-offline-sync` · `qrafig-outbox-jobs` · `qrafig-inventory`.
