---
name: qrafig-testing
description: Write and run QRAFIG's tests correctly — the four suites and what each can and cannot prove, the real-PostgreSQL integration harness, independent-client concurrency tests, Desktop view-model tests without a dispatcher, real-API end-to-end tests, reproduction-first discipline, and the classes of defect no test in this repository can catch. Use whenever adding or changing a test, deciding what proof a change needs, or diagnosing a suite that fails for environmental reasons.
when_to_use: Writing tests, choosing which suite a test belongs in, integration or Testcontainers problems, "prove this works", mass test failures that look environmental.
---

# Testing QRAFIG

## Read first

- `backend/tests/Qrafig.IntegrationTests/ApiFactory.cs`, `TestClient.cs`, `AuthFlow.cs`.
- The nearest existing test file for the area you are changing — it states the invariants more
  precisely than any prose.
- `desktop/tests/Qrafig.Desktop.Tests/FakeApi.cs`, `PosTillHarness.cs`, `SqliteCollection.cs`.
- `desktop/tests/Qrafig.Desktop.EndToEndTests/LiveApiFixture.cs`.
- `docs/implementation-status.md` → `## Test inventory` for the current counts.
- ADRs 0018, 0132, 0190, 0191.

## The four suites

| Project | Runs | Proves | Cannot prove |
| --- | --- | --- | --- |
| `backend/tests/Qrafig.UnitTests` | no Docker | pure domain arithmetic and invariants — money boundaries, quantity rounding, permission catalog, refresh-token state | anything involving the database |
| `backend/tests/Qrafig.IntegrationTests` | Docker: PostgreSQL 18 + Redis 8 via Testcontainers | the real HTTP surface against real PostgreSQL: unique and partial indexes, `numeric(18,3)`, concurrency tokens, advisory locks, migrations | anything about rendering, and anything about a real client's disk |
| `desktop/tests/Qrafig.Desktop.Tests` | no Docker; Windows for DPAPI cases | view models, navigation resolution, the local SQLite database and its migrations, device lifecycle, offline cold start against real DPAPI files | **anything WPF resolves at run time** — a `StaticResource`, a `DataContext`, a `Trigger`, a command's enabled state, layout |
| `desktop/tests/Qrafig.Desktop.EndToEndTests` | Docker + the real API over real HTTP | the shipped client against the real server, including two tills at one shop | the same rendering gap |

**Run them separately.** A whole-solution `dotnet test` starts a container pair per integration test
class — around fifty at once — and takes the Docker daemon down mid-run. The symptom is
~900 integration failures at `RegisterAndLoginAsync` with `500` while the Desktop suites pass. That is
the environment, not the code.

## The integration harness

`ApiFactory : WebApplicationFactory<Program>, IAsyncLifetime` hosts the API against real containers
(ADR-0018). Points that are easy to get wrong:

- Configuration overrides use **`builder.UseSetting`**, not `ConfigureAppConfiguration`. With top-level
  statements the entry point reads `builder.Configuration` before `ConfigureAppConfiguration`
  callbacks run, so those overrides arrive too late and the host silently falls back to
  `appsettings.Development.json` — which points at the developer's Compose database.
- The host is touched in `InitializeAsync` so a **migration failure surfaces as a setup error**
  rather than as a confusing first-test failure.
- Object storage gets its own temporary root per run.
- Jobs and the outbox worker are **off** in tests (`Jobs:Enabled=false`, `Outbox:Enabled=false`); a
  timer racing the suite would make failures depend on when they ran. Tests drive the same dispatcher
  directly.
- Helpers live in `TestClient.cs` (`RegisterAndLoginAsync`, `PostJsonAsync`, `ReadJsonAsync`,
  `UniqueSlug`) and `AuthFlow.cs`. Use them; do not hand-roll a second registration path.

## Concurrency tests

Use **independent `HttpClient` instances**. Two awaited calls on one client serialize in the client
and prove nothing.

```csharp
private HttpClient SecondClient(Shop shop)
{
    var client = factory.CreateClient();
    var auth = shop.Client.DefaultRequestHeaders.Authorization!;
    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue(auth.Scheme, auth.Parameter);
    return client;   // separate connection, scope and DbContext
}

var results = await Task.WhenAll(Clients(shop, 6).Select(c => c.PostJsonAsync(route, body)));
```

Assert the **invariant** — exactly one row, the ledger still sums to the balance, nothing oversold, no
`500` — rather than a particular pair of status codes.

## Reproduction first

Write the failing test **before** the fix, and check that it fails against the current implementation.
QRAFIG's own precedent: the whole `CustomerConcurrencyTests` file fails on the released code, and the
credit-ceiling defect was proved by two tills both selling 7,000 on account against a 10,000 limit and
both getting `201`. A race test that passes before the fix is testing something else.

## Naming and organizing

Tests are organized around **what can go wrong**, not around the API surface. The repository's own
split is worth copying:

- `…Tests` — the ordinary contract.
- `…ConcurrencyTests` — genuine overlapping requests.
- `…InvariantTests` — the semantics that are decisions rather than arithmetic (a supplier invoice is
  debt and its payment is cash flow and neither is an expense; a DST day is 23 or 25 hours).
- `…ContractTests` / `MirroredContractTests` — the wire shape and the client's copy of it.
- `…VerticalSliceTests` (end to end) — the real client against the real API.

Give each test a sentence-shaped name that states the claim.

## Desktop tests

- View models live in a project with **no UI framework**, which is what lets them run headless. Keep
  it that way; use the `IUiThread` port rather than a dispatcher (ADR-0132). Unset, it runs inline,
  which is exactly right for a test.
- `CompositionRootTests` builds the container the shipped application actually builds and **resolves**
  the graph — a descriptor list can be complete and still have a cycle or a missing transitive
  dependency, and that is how the POS freshness worker's wiring first reached the executable
  unverified.
- `MirroredContractTests` is the one place the client references the server's assembly, and exists
  only to compare permission, feature and error code strings.
- `LocalDatabaseTests` / `LocalMigrationTests` cover the `user_version` migration chain.
- `SqliteCollection` serializes tests that share a database file.
- `FakeApi.cs` and `PosTillHarness.cs` are the fixtures — extend them rather than adding a third.

## What no test here can catch

WPF resolution, theming and liveness — a missing `StaticResource`, a `DataContext` override that
shadows a sibling binding, a `Trigger` that never matches, a control with no style, a command that
never re-asks whether it may execute, an `Auto` column that starves its neighbour. Nine of eleven
defects found in one live run were invisible to every test in the repository (ADR-0191). That gap is
covered by `qrafig-desktop-live-smoke`, not by adding more headless tests.

## Environment

- Linux needs `-p:EnableWindowsTargeting=true` to build the WPF project, and **DPAPI cases throw
  `PlatformNotSupportedException`** there. On Windows the baseline is zero such failures.
- A restricted container may need `mirror.gcr.io` for images and `TESTCONTAINERS_RYUK_DISABLED=true`.
- Docker-backed suites never touch the developer's Compose database.

## Verification

The suite you added to runs green, and the suite that *should* have caught the defect earlier is
either extended or explicitly named as unable to. For a fix, the new test **fails on the code before
the fix**; check that, do not assume it. Then run the other three projects, because a contract change
usually reaches more than one. Record which projects you ran and on which platform.

## Do not

- Do not skip, disable or quarantine a test to reach green.
- Do not weaken an assertion to fit a change.
- Do not add `Thread.Sleep` or an ordering hack to make a race reproduce.
- Do not introduce a mocking framework or a provider-less database fake for behaviour that only real
  PostgreSQL exhibits — that is the whole reason for ADR-0018.
- Do not assert on `title` or `detail` of a Problem Details response; assert on `code`.

## Related skills

`qrafig-verification` (which gates apply) · `qrafig-concurrency` · `qrafig-desktop-live-smoke` ·
`qrafig-diagnostics` · `qrafig-efcore-migrations`.
External: Testcontainers for .NET — see `docs/ai/sources.md`.
