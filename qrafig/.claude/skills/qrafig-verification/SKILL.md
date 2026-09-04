---
name: qrafig-verification
description: The QRAFIG definition of done and the gate matrix — which build, test, migration, concurrency, tenant-isolation, live-WPF and supply-chain gates a given change class must pass, how to run the four test projects correctly, which gates a Linux container cannot run, and how to report results honestly. Use before claiming any QRAFIG work is finished, and when deciding what proof a change needs.
when_to_use: Before reporting completion; when asked "check the whole module before production"; when deciding whether a change needs a migration check, a concurrency test, a cross-tenant test or a live QRAFIG.exe smoke.
---

# The QRAFIG verification gate

"It compiles", "one test passed" and "this is the standard pattern" are not evidence. QRAFIG's own
history is the argument: a Linux build of the Desktop project passed and the next Windows run found
eleven defects in the same markup, nine of which no test in the repository could catch (ADR-0191).

## Read first

- `README.md` § *Verification* — the four gate commands.
- `docs/implementation-status.md` → the handoff's *Current failing command*, the verification-commands
  block, and `## Test inventory` for the **current** expected counts.
- `docs/api-roadmap.md` § *Cross-client Definition of Done*.
- `Directory.Build.props` (`TreatWarningsAsErrors`) and `Directory.Packages.props`.

## The base gate — every change

```bash
dotnet restore --force-evaluate
dotnet build                                   # must be 0 warnings, 0 errors
```

`TreatWarningsAsErrors=true` is set in `Directory.Build.props`. Never suppress a warning to make the
build green; fix the cause.

## The four test projects — run them separately

```bash
dotnet test backend/tests/Qrafig.UnitTests                # no Docker
dotnet test backend/tests/Qrafig.IntegrationTests         # Docker: PostgreSQL 18 + Redis 8
dotnet test desktop/tests/Qrafig.Desktop.Tests            # no Docker; needs Windows for DPAPI cases
dotnet test desktop/tests/Qrafig.Desktop.EndToEndTests    # Docker + the real API over real HTTP
```

**A whole-solution `dotnet test` is a trap.** It starts a PostgreSQL and a Redis container per
integration test class — around fifty at once at default xUnit parallelism — and takes the Docker
daemon down mid-run. The symptom is misleading: the Desktop suites pass while hundreds of integration
tests fail at `RegisterAndLoginAsync` with `500`. That is environmental, not a code failure.

Read the **current** expected counts from `docs/implementation-status.md`. Do not hard-code a number
from anywhere else, including from this file.

## The gate matrix

| Change class | Additional mandatory gates |
| --- | --- |
| **Domain / application logic** | Backend unit + backend integration. If persistence changed, the migration gates below. |
| **New or changed endpoint** | Backend integration covering: success, validation failure, **missing permission (403)**, **non-member (404, never 403)**, and **cross-tenant** (organization A cannot read or influence B). `OpenApiTests` must stay green. |
| **Entity, configuration, index or schema** | `dotnet ef migrations has-pending-model-changes` reports no changes; migration applies to a **fresh** database; migration applies **in sequence onto a populated database of the previous phase**; integration tests green. |
| **Any read-modify-write, claim, counter, uniqueness rule or status transition** | A concurrency test firing **independent `HttpClient` instances** at the endpoint simultaneously. Two awaited calls on one client serialize in the client and prove nothing. |
| **Money** | Boundary values including `long.MinValue`, `long.MaxValue` and `MoneyArithmetic.MaxAbsoluteMinor`; a second currency; a concurrent mutation of one balance; a backdated entry reported in the period it happened in; a DST day proved 23 or 25 hours long. |
| **Authorization or roles** | Positive, negative, cross-tenant, **and stale-authority** cases — a token minted before a suspension must still be refused by the live re-read. |
| **Offline / POS capture** | Disconnected capture, retry, duplicate push settling as `duplicate` rather than `500`, crash and restart with the operation still queued, reconnect, and server reconciliation written **beside** the local record. |
| **Outbox handler or job** | At-least-once delivery proved; handler idempotency proved independently of the unique index; retry classification (retryable vs permanent) proved; dead-letter path proved. |
| **XAML, view, resource dictionary, converter, command, shell or navigation** | Desktop view-model tests + **a live `QRAFIG.exe` smoke on Windows** — see `qrafig-desktop-live-smoke`. Mandatory, not optional. |
| **A contract the Desktop client mirrors** (permission, feature or error code) | `MirroredContractTests` — the one place the client references the server's assembly. |
| **Composition root / DI registration** | `CompositionRootTests` resolves the real graph; a missing transitive dependency compiles and passes every unit test. |
| **Dependency change** | `dotnet list package --vulnerable --include-transitive` reports none. |
| **Performance work** | A measurement before and after, on the same data shape. A claim without a number is not a result. |
| **Site (separate repository)** | `npx tsc --noEmit`, `npx eslint .`, `npm run build`; see `qrafig-site`. |

## The persistence gates in full

```bash
dotnet ef migrations has-pending-model-changes \
  --project backend/src/Qrafig.Infrastructure \
  --startup-project backend/src/Qrafig.Api          # must report no changes
```

A new migration must also be shown to apply **onto a populated database**, not only onto an empty one.
The integration suite applies migrations at host start, so a fresh-database failure surfaces as a
setup error; a populated-database failure will not surface there at all. See `qrafig-efcore-migrations`.

## Supply chain

```bash
dotnet list package --vulnerable --include-transitive
```

Transitive pinning is enabled centrally (`Directory.Packages.props`), so a single `PackageVersion`
entry moves every consumer. That is the correct place to pin a transitive advisory fix.

## What a Linux container cannot do

Record this honestly rather than working around it:

- `dotnet build` of the WPF project needs `-p:EnableWindowsTargeting=true` on Linux.
- **DPAPI (`ProtectedData`) has no Linux implementation.** Cases that exercise the device credential,
  offline sign-in material or remember-me throw `PlatformNotSupportedException` there. On Windows the
  baseline is **zero** such failures, so a DPAPI failure on Windows is a real regression.
- The **live `QRAFIG.exe` smoke cannot run on Linux at all**.
- Testcontainers may need `mirror.gcr.io` and `TESTCONTAINERS_RYUK_DISABLED=true` in a restricted
  container.

## Reporting

State, for each gate: run / not run, and the result. For a gate you could not run, say which and why
("no Windows host, so the live smoke and the DPAPI cases did not run"). Then say plainly what is
therefore unproven.

Never write "all tests pass" when you ran one project. Never write "verified" for a gate you skipped.
Never mark a Desktop workspace complete without the live smoke.

## Do not

- Do not skip, disable, `[Fact(Skip=…)]` or quarantine a test to get to green.
- Do not weaken an assertion to make a change fit; change the code or change the contract deliberately.
- Do not hand-edit `QrafigDbContextModelSnapshot.cs` to make the pending-model check pass.
- Do not relax a security or tenancy check to make a test pass.
- Do not report a count you did not observe.

## Related skills

`qrafig-testing` (how to write the tests) · `qrafig-desktop-live-smoke` (the live gate) ·
`qrafig-efcore-migrations` · `qrafig-concurrency` · `qrafig-tenancy`.
