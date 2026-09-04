---
name: qrafig-architecture
description: QRAFIG's structural rules — the five-project layer topology and what may reference what, modular-monolith module boundaries, identifiers and value types, contract versioning and released error codes, where a new module or service belongs, and how to record a decision as an ADR without rewriting history. Use when a change crosses a layer boundary, adds a module or service, alters a released contract, or is significant enough to owe an architecture decision record.
when_to_use: Adding a module, moving code between projects, changing a released wire contract or error code, deciding where something belongs, or writing an ADR.
---

# QRAFIG architecture

QRAFIG is a **modular monolith**, not microservices (ADR-0001). Modules are namespaces and folders
inside shared projects, not deployable units. Do not introduce a service boundary, a queue between
modules or a second database because a module felt large.

## Read first

- `Qrafig.sln`, `Directory.Build.props`, `Directory.Packages.props`.
- `docs/api-roadmap.md` §§ *Canonical source hierarchy*, *Global engineering contract*.
- `backend/src/Qrafig.Application/Abstractions/IQrafigDbContext.cs`.
- The nearest existing module to the one you are adding to.
- ADRs 0001, 0002, 0003, 0009, 0014, 0017.

## Layer topology (ADR-0002) — read first

```
backend/src/Qrafig.Domain          entities, value objects, invariants.   No EF, no ASP.NET.
backend/src/Qrafig.Application     services, contracts, validation, permission codes.
                                   Depends on Domain and on IQrafigDbContext only.
backend/src/Qrafig.Infrastructure  EF Core, PostgreSQL, Redis, security, adapters, storage.
backend/src/Qrafig.Api             endpoint modules, middleware, composition root.
backend/src/Qrafig.Workers         background / outbox host.
```

Desktop mirrors the same idea:

```
desktop/src/Qrafig.Desktop.Contracts       client mirrors of the API's wire contracts
desktop/src/Qrafig.Desktop.Application     use cases, client context, view models. NO UI framework.
desktop/src/Qrafig.Desktop.Infrastructure  HTTP transport, local SQLite, DPAPI, DI root
desktop/src/Qrafig.Desktop                 WPF shell, views, design system → QRAFIG.exe
```

The **no-UI-framework rule** on `Qrafig.Desktop.Application` is load-bearing: it is what lets a
thousand view-model tests run headless. A `PresentationCore` type dragged into that project drags a
dispatcher with it. When you need a UI-thread guarantee there, use the existing `IUiThread` port
(ADR-0132), never `Dispatcher` directly.

The Application layer does not reference a database provider. Recognising a PostgreSQL error code
therefore happens behind `IQrafigDbContext.IsUniqueViolation(exception, constraintName)`, which takes
the **constraint name** on purpose — treating any `23505` as your expected collision swallows another
index's refusal and reports success for work the database rejected (ADR-0129).

## Rules that hold everywhere (`docs/api-roadmap.md` § Global engineering contract)

| Concern | Rule |
| --- | --- |
| Target | `net10.0`, `TreatWarningsAsErrors=true` |
| Identifiers | `Guid.CreateVersion7()` in application code. No database `DEFAULT`, no `SERIAL`. Client-supplied ids only where the offline protocol requires them (`operation_id`) — ADR-0003 |
| Timestamps | UTC `timestamptz` / `DateTimeOffset` |
| Money | `bigint` minor units + ISO 4217 code — ADR-0004 |
| Quantities | `numeric(18,3)` — ADR-0005 |
| Persistence | Explicit `IEntityTypeConfiguration<T>` per entity; snake_case tables and columns |
| Transport | Request/response contracts only. **EF entities never leave the Application layer.** |
| Errors | RFC 9457 Problem Details with a stable machine-readable `code` — ADR-0009 |
| Pagination | Cursor pagination for large mutable collections — ADR-0016 |
| Concurrency | Optimistic concurrency via `row_version` where mutation races matter — ADR-0008 |
| Immutability | Financial documents and completed sales are append-only — ADR-0007 |
| Inventory | Balance is derived from movements, never overwritten — ADR-0006 |
| Post-commit work | Transactional outbox — ADR-0015 |
| Sync | Every operation idempotent by `operation_id` — ADR-0047 |
| Country logic | Behind a Country Pack / adapter, never scattered conditionals |
| Providers | External providers behind adapters; development providers are labelled as such — ADR-0014 |

## Where things go

- A **new endpoint** goes in the existing module file under `backend/src/Qrafig.Api/Endpoints/`, not
  in a new one and not in a shared `Endpoints.cs` (ADR-0017).
- A **new business rule** goes in `Qrafig.Domain` if it is an invariant of an entity, and in
  `Qrafig.Application` if it coordinates several.
- **Anything provider-specific** — SQL, Redis, S3, JWT, Argon2 — goes in `Qrafig.Infrastructure`
  behind an abstraction declared in `Qrafig.Application/Abstractions`.
- A **client mirror** of a permission, feature or error code goes in `Qrafig.Desktop.Application`
  and is pinned by `MirroredContractTests`. The client copies these strings deliberately (an
  installed client is upgraded on the user's schedule) — so the test that compares them is the whole
  justification for the copy being safe (ADR-0109).

## Released contracts

An error code is a **released contract** once a client can see it. Codes never change meaning
(ADR-0009); clients branch on `code`, never on `title` or `detail`. Adding a code is cheap; changing
one is a breaking change. The same is true of a permission code, a feature code and a wire field the
Desktop client mirrors.

When a contract has to change:

1. add the new shape alongside the old one;
2. move the clients;
3. remove the old one in a later change, with the ledger recording it.

Additive reporting is the pattern QRAFIG already uses for exactly this — shift accounting after a
close adds `reconciled*` fields rather than changing what `expectedCashMinor` means (ADR-0127).

## Writing an ADR

`docs/architecture-decisions.md` is **append-only**. A later ADR supersedes an earlier one; history is
never rewritten and numbers never change meaning.

Write one when your change: makes a choice a future reader could reasonably reverse by accident;
constrains other modules; trades one failure mode for another; or records something learned the hard
way (several of QRAFIG's best ADRs are post-mortems).

Structure, following the file's own convention:

```markdown
## ADR-NNNN — A one-sentence claim, stated as the decision

**Status.** Accepted, YYYY-MM-DD.            (only where neighbours use it)

**Context.** What was true, what went wrong or what forced the choice. Name the concrete failure.

**Decision.** What is done now, precisely enough to be checked against the code.

**Consequences.** What this costs, what is now guaranteed, what tests pin it, and what it does
**not** promise.
```

If you are superseding, say so in the first line (`**Supersedes ADR-0188.**`) and leave the old record
untouched. If you are correcting, add a correcting ADR the way ADR-0038 corrects ADR-0035 and ADR-0036.

## Failure modes

- **Reaching for a new project or service** because a folder got big. The monolith is a decision.
- **Leaking an EF entity into a response.** It ties the wire to the schema and exposes fields the
  contract never promised (`rowVersion`, internal ids, cost).
- **Putting a provider concern in Application** — a `Npgsql` type, an S3 client, a `SqlException`.
- **Re-deriving tenant access** in a service instead of going through `OrganizationContext`.
- **Editing an ADR** to make it agree with new code.
- **Changing an error code's meaning** because a new caller wanted a different word.
- **Adding a second authority**: a client, cache or projection that computes a permission, a balance
  or a price rather than reading the server's answer.

## Verification

Build with zero warnings; the relevant suites; `MirroredContractTests` if a mirrored constant moved;
`CompositionRootTests` if registration changed; `OpenApiTests` if the surface changed. If you wrote an
ADR, cite its number in the code that honours it — `grep -rn 'ADR-0' backend/src` shows the convention.

## Do not

- Do not add a project, service or second database because a folder grew.
- Do not let an EF entity reach the wire.
- Do not put a provider concern in `Qrafig.Application`.
- Do not re-derive tenant access outside `OrganizationContext`.
- Do not edit an ADR in place — supersede it.
- Do not change the meaning of a released error, permission or feature code.
- Do not reference a UI framework from `Qrafig.Desktop.Application`.
- Do not add a second authority that computes a permission, price or balance the server owns.

## Related skills

`qrafig-api-endpoints` · `qrafig-efcore-migrations` · `qrafig-repo-state` (finding the governing ADR)
· `qrafig-concurrency` · `qrafig-desktop-workspace`.
