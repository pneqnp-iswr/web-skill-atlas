---
name: qrafig-router
description: Start here for any QRAFIG development task. Decides which parts of the repository to inspect, which QRAFIG and external skills to load, which ADRs and status sections to read, which invariants apply, which tests and gates are mandatory, and whether a live QRAFIG.exe smoke, a migration check, a concurrency test, a tenant-isolation review or a performance measurement is required. Use it for open-ended requests ("continue QRAFIG", "work out what is broken and fix it"), for short requests that hide several domains ("add a refund button", "make Reports"), and whenever you are unsure which skill applies. Do not use it for questions about the marketing site alone.
when_to_use: Any request to build, fix, review, audit, extend, optimize or continue QRAFIG. Trigger phrases include "сделай", "почини", "добавь", "проверь", "разберись", "продолжи разработку", "add endpoint", "new migration", "fix this page", "security audit", "find race conditions", "optimize", "before production".
---

# QRAFIG task router

Routing is a **decomposition**, not a keyword lookup. Most real requests touch three to six domains.
A request that mentions one word ("refund") can require WPF, POS, permissions, finance, offline
behaviour, sync and four test suites. Decompose first, then load.

## Read first

Nothing here — routing decides what to read. Step 1 sends you to `qrafig-repo-state`, and each lane's
skill carries its own **Read first** list.

## Step 1 — Orient (always, no exceptions)

Load `qrafig-repo-state` and do what it says. In short:

1. `docs/implementation-status.md` → `## Session handoff`. Read **Last completed task**,
   **Current failing command**, **Next concrete task**, **Planned next Desktop slice**.
2. Decide whether the request is inside a **closed claim** (a "Functional Alpha complete" row). If it
   is, and the user did not ask you to reopen it, say so and scope the work outside it.
3. If the request is open-ended ("continue"), the handoff's *Next concrete task* is the answer. Do not
   invent a different one and do not restart a delivered phase.

## Step 2 — Decompose the request into signals

Ask these questions of the request, not of its wording. Each **yes** adds a lane.

| Question | Lane |
| --- | --- |
| Does it change or read HTTP surface (route, contract, status, error code, OpenAPI)? | **API** |
| Does it change entities, configuration, indexes or schema? | **Persistence** |
| Does it change money, balances, approvals, transfers or reconciliation? | **Finance** |
| Does it change what a till captures, or what a shift/drawer/receipt means? | **POS** |
| Can the operation happen while the server is unreachable, or be replayed later? | **Offline/Sync** |
| Does it change stock, movements, transfers, stocktakes or holds? | **Inventory** |
| Does it involve suppliers, purchase orders, goods receipts or landed cost? | **Purchasing** |
| Does it touch customer identity, debt, loyalty, certificates or personal data? | **Customers** |
| Does it aggregate across a business or a period? | **Reporting** |
| Does it decide who may do something? | **Authorization** |
| Could organization A observe or influence organization B — or location A location B? | **Tenancy** |
| Does it handle credentials, tokens, hashes, signed material, PII or logs? | **AppSec** |
| Is there a read-modify-write, a claim, an insert-after-check, or a shared counter? | **Concurrency** |
| Does it emit post-commit effects (events, webhooks, notifications, jobs)? | **Outbox/Jobs** |
| Does it move bytes into or out of object storage? | **Storage** |
| Does it touch XAML, a view, a view model, navigation or the shell? | **Desktop** |
| Is it about speed, memory, payload size or a query plan? | **Performance** |
| Is the symptom only visible at runtime, or is the cause unknown? | **Diagnostics** |
| Is it the marketing site? | **Site** (and *nothing else on this table*) |

## Step 3 — Load skills from the lanes

| Lane | Load | Also load when |
| --- | --- | --- |
| API | `qrafig-api-endpoints` | + `qrafig-tenancy` and `qrafig-authorization` for every new or changed route, always |
| Persistence | `qrafig-efcore-migrations`, `qrafig-postgres` | + `qrafig-concurrency` if the change adds a uniqueness rule, a counter or a status transition |
| Finance | `qrafig-money-finance` | + `qrafig-concurrency` (balances are contended by construction) |
| POS | `qrafig-pos-domain` | + `qrafig-offline-sync` unless the operation is provably online-only |
| Offline/Sync | `qrafig-offline-sync`, `qrafig-sqlite-local` | + `qrafig-pos-domain` if the operation is a till operation |
| Inventory | `qrafig-inventory` | + `qrafig-concurrency` for any balance-affecting path |
| Purchasing | `qrafig-purchasing` | + `qrafig-money-finance` when supplier debt or payment is involved |
| Customers | `qrafig-customers-privacy` | + `qrafig-appsec` for export, erasure or anything leaving the system |
| Reporting | `qrafig-reporting` | + `qrafig-money-finance` for any monetary figure; + `qrafig-performance` for a new aggregate |
| Authorization | `qrafig-authorization` | |
| Tenancy | `qrafig-tenancy` | |
| AppSec | `qrafig-appsec` | |
| Concurrency | `qrafig-concurrency` | + `qrafig-postgres` |
| Outbox/Jobs | `qrafig-outbox-jobs` | + `qrafig-observability` when adding a handler or a job |
| Storage | `qrafig-storage` | + `qrafig-appsec` (signed URLs are credentials) |
| Desktop — markup or rendering only | `qrafig-desktop-wpf` | + `qrafig-desktop-live-smoke` (always, per Step 5). **Not** `qrafig-desktop-workspace` for a pure layout, style or trigger fix |
| Desktop — behaviour, navigation, state or contract | `qrafig-desktop-workspace` | + `qrafig-desktop-wpf` if markup changes too; + `qrafig-desktop-live-smoke`; + the domain skill the workspace serves |
| Performance | `qrafig-performance` | + the skill owning the layer being measured |
| Diagnostics | `qrafig-diagnostics` | + the skill owning the suspected layer, after the reproduction |
| Site | `qrafig-site` | nothing else |

`qrafig-architecture` loads when the change crosses a layer boundary, adds a module, changes a
released contract, or is large enough that an ADR is owed. `qrafig-testing` loads whenever you will
write or change a test, which is almost always. `qrafig-verification` loads before you report.

## Step 4 — Read first

Every lane's skill has its own **Read first** list. On top of them, always read:

- the endpoint module or view that already does the nearest thing — QRAFIG is highly patterned, and
  the nearest neighbour is usually the specification;
- its tests, which state the invariants more precisely than prose;
- the ADRs the area names. Find them with
  `grep -n '^## ADR-' docs/architecture-decisions.md | grep -i '<topic>'`, then read the hits and
  anything they supersede.

## Step 5 — Decide the gates

Load `qrafig-verification` for the full matrix. The four questions that decide the expensive gates:

1. **Did persistence change?** → `dotnet ef migrations has-pending-model-changes` must report no
   changes, and a new migration must be applied to a *populated* database, not only a fresh one.
2. **Is there a read-modify-write, a claim, or a uniqueness rule?** → a concurrency test with
   **independent `HttpClient` instances** is mandatory. Two calls on one client prove nothing.
3. **Did XAML, a view, a resource dictionary, a converter, a command or the shell change?** → a live
   `QRAFIG.exe` smoke on Windows is mandatory (ADR-0191). Compiling is evidence about names only.
4. **Did a route, a query, a cache key, a file path, a job or an exported document change?** → a
   cross-tenant negative test is mandatory.

## Step 6 — Report honestly

Name the gates you ran and their results, and the gates you could **not** run and why (no Windows, no
Docker, no live server). Never present an unrun gate as passed.

## Worked decompositions

**"Add a refund button"** → POS + Finance + Authorization + Offline/Sync + Desktop + Concurrency.
Read: `ReturnEndpoints.cs`, `Application/Returns/*`, `PosReturnViewModel`, `PosReturnView.xaml`,
ADR-0057 – ADR-0061, ADR-0120, ADR-0123. Invariants: a return unwinds what the sale took, not what
the refund gives; a return needing approval moves nothing until approved; a manager authorizes one
decision and never takes the till. Gates: backend integration + Desktop view-model + E2E + **live
smoke** + a concurrency test on approval racing refusal.

**"Fix offline sync"** → Offline/Sync + POS + Concurrency + Persistence + Diagnostics.
Read: `Application/Sync/*`, `SqliteOperationQueue`, `DeviceSyncChannel`, ADR-0047, ADR-0048,
ADR-0054, ADR-0113, ADR-0118, ADR-0129. Reproduce before fixing. Gates: `OfflineSalesTests`,
`SyncTests`, `PosSaleSyncTests`, `PosReconciliationTests`, plus crash/restart and duplicate-push cases.

**"Make Reports"** → Reporting + Finance + Authorization + Tenancy + Desktop + Performance.
Read the handoff (Reports is the named next Desktop slice and is feature-gated `reports`, outside the
trial plan — so the first question the slice answers is *what a locked module shows*), ADR-0069 –
ADR-0076, `Application/Reporting/*`, `ReportEndpoints.cs`, `LockedModuleView.xaml`, and the promise
the Customers and Finance overviews already make about Reports. Gates: all four suites + live smoke.

**"Optimize a PostgreSQL query"** → Performance + Persistence. Do **not** load POS, Finance, Desktop
or Site. Measure first with a plan, change one thing, measure again, and check the change did not
weaken an index another path depends on.

**"Fix metadata on the site"** → Site only. Do not load POS, Finance, SQLite, EF Core or anything
else on this page.

**"Continue QRAFIG"** → Step 1 answers it. The handoff's *Next concrete task* is the task.

## Negative routing — what not to load

- A **site** change never loads a backend, Desktop, database or domain skill. The site shares nothing
  with the platform but brand values.
- A **PostgreSQL deadlock** never loads `qrafig-site`, `qrafig-desktop-wpf` or any visual skill.
- A **XAML clipping** fix never triggers a migration, an EF check or a database skill.
- A **favicon, icon or asset** change loads nothing from Finance, POS or Inventory.
- A **backend-only** change loads no Desktop skill and needs no live smoke — but *does* need one if it
  changed a contract the client mirrors (`MirroredContractTests` is the tripwire).
- **Never** load every skill "to be safe". Loaded context you do not use is context you do not have
  for the work.

## Do not

- Do not route on a single keyword — decompose into lanes.
- Do not load every skill "to be safe"; unused context is context you do not have for the work.
- Do not load a platform skill for a site task, or a site skill for a platform task.
- Do not skip Step 1 because the request looks small.
- Do not start work inside a closed claim, or a phase the handoff says not to start.
- Do not report before running Step 5's gates, or without saying which you could not run.

## Related skills

`qrafig-repo-state` (state and claims) · `qrafig-verification` (gates) · `qrafig-architecture`
(boundaries and ADRs) · `qrafig-diagnostics` (unknown cause). External sources: `docs/ai/sources.md`.
