---
name: qrafig-desktop-workspace
description: Add or change a QRAFIG Desktop workspace — the ten workspaces and the navigation model computed from the server-resolved client context, the four access states that must never be conflated, the mirrored permission/feature/error codes, the view-model conventions (command re-raising, ObservableList and the UI thread, explicit Save versus immediate posting), online-only versus offline-capable modules, the composition root, and organization-switch and restart safety. Use when building a new workspace or surface, changing navigation, or wiring a view model to the API.
when_to_use: New Desktop workspace or surface, navigation and sidebar, locked or not-built states, client context, view-model wiring, DI registration, offline capability of a module, organization switch.
---

# Building a QRAFIG Desktop workspace

One installed Windows application, **ten workspaces** — `Home`, `Pos`, `Catalog`, `Warehouse`,
`Purchasing`, `Customers`, `Finance`, `Employees`, `Reports`, `Settings` — inside one `QRAFIG.exe`
(ADR-0109). A launch mode chooses a starting workspace; it grants nothing.

## The client renders decisions; it does not make them

`ClientContext` is assembled **only** from server responses — the effective permission set from
`GET /organizations`, the feature codes from `GET /organizations/{id}/subscription/entitlement`, the
locations from the store list — and computes **no authorization of its own**. Every privileged call
still goes to the server and must survive being refused there. **Hiding a control is a courtesy to the
user, never a boundary.**

A context that derived its own permissions would be a second, divergent authorization implementation
shipped to the least trustworthy machine in the system.

The client **mirrors** permission, feature and error code strings rather than referencing the server's
assembly, because an installed client is upgraded on the user's schedule and must tolerate a server
that has added a field. The cost is that a typo is silent — so `MirroredContractTests` is the one
place the server's assembly *is* referenced, and it exists only to compare those strings. **Add your
new code to the mirror.**

The summary endpoint describes the authority the endpoints enforce, including operational policy the
client cannot derive (ADR-0133). Read it; do not re-derive it.

## Four access states, never conflated

`AccessState` in `Navigation/NavigationModel.cs`. The order the checks run in **is** the decision:

1. **`PermissionDenied`** — the organization owns the capability; this employee may not use it. **Asked
   first.** No pricing, no upgrade call to action, not even for an owner: the plan is not the obstacle,
   and mentioning it sends the reader to the wrong person with a question they cannot act on.
2. **`EntitlementUnavailable`** — the organization has not bought the module. For an owner or a holder
   of `subscription.manage` this is a premium locked state that can route to an upgrade; for everybody
   else it is "not active for your organization".
3. **`Offline`** — neither of the above; the capability needs the server and the server is unreachable,
   so what is true about it is currently **unknown**. With a stale entitlement this **outranks the
   lock**: telling somebody their plan lacks something they may have bought an hour ago is the worst of
   the three mistakes — it is wrong, it is about money, and they cannot check.
4. **`NotBuilt`** — permitted, paid for and unbuilt in this release. It **says so** (`NotBuiltView`). A
   blank page styled to look finished would be a claim that the module exists.

Navigation is built from the server-resolved context and is a **pure function of it**, so it is
testable with no window (`NavigationTests`).

**Every state must be reachable by every path that leads to it.** The shell's hosts swap on `HasLock`,
and once only navigation ever filled the lock host — so a workspace that became unreachable *where it
stood*, the connection dropping while somebody was in it, went completely blank. When you add a state,
enumerate the paths into it and check each.

## View-model conventions

- Live in `Qrafig.Desktop.Application`, which has **no UI-framework reference**. Keep it that way.
- **Commands must be told when their `CanExecute` inputs changed** (ADR-0190). Prefer the Customers
  pattern: subscribe to your own `PropertyChanged` and re-raise **every** command from there — one call
  site that cannot miss a dependency. A command reading another view model's state subscribes to that
  one. The alternative (a `RaiseCanExecuteChanged()` beside each assignment) is what produced the
  defect; if you use it, you own the obligation at every mutation site.
- **Bound collections change on the UI thread.** Use `ObservableList<T>` and the `IUiThread` port; WPF
  marshals `PropertyChanged` but **not** `CollectionChanged` (ADR-0132).
- **Save policy** (`docs/client-save-policy.md`): ordinary forms — product cards, employee profiles,
  settings — hold edits in local state until **Save**, mark unsaved changes, confirm before discarding,
  and send **one complete command** that the server commits atomically with a `rowVersion` check
  (ADR-0114: one row-version check, one `SaveChangesAsync`, all or none). Critical business
  operations — sales, payments, stock movements, receipts, transfers, role changes, shift open/close —
  post **immediately** and durably.
- **A save names the version it was composed against.** A lost answer is **replayed under the same
  key**, never re-composed.
- **Re-read authoritatively** after a command rather than patching the local row from the response.
- A pending or refused state is shown as what it is: a pending expense is **waiting, not spent**.
- An editor **says nothing is wrong until something is**.

## Online-only versus offline-capable

Decide this explicitly and record it. Currently online-only **by decision, with no local table and no
queue** — the absence is the mechanism: Warehouse mutations (ADR-0142), Transfers (ADR-0149), Customers
Backoffice (ADR-0185), Finance (ADR-0203), Employees (ADR-0207). Offline-capable: the till's capture
path, and read-only cached boards where an ADR says so.

Something has to ask whether the server is back — the reconnect probe (ADR-0204) — and the workspace
must **come back on its own**, not after somebody presses Refresh. A rebuild that goes through a
workspace's own re-selection guard can *reveal* a stale workspace rather than replacing it; check that.

## Composition and startup

- Register in `DesktopServices` / `AddQrafigDesktop`. `CompositionRootTests` **resolves** the real
  graph — a descriptor list can be complete and still have a cycle or a missing transitive dependency,
  which is how the POS freshness worker's wiring first reached the executable unverified.
- `ShellViewModel.StartAsync` loads **device identity first**, before the session and before any early
  return, with **no `.Result` anywhere** (ADR-0110).
- Device identity has **four** states — `NotInitialized`, `NotActivated`, `Activated`,
  `CredentialUnreadable`. "Not yet asked" is not an answer.
- **Unknown is a value and never grants anything** (ADR-0115): `AllowsNewWork` is `bool?`, connectivity
  has one author, and a failed projection of a claimed type keeps the cursor.
- `remember=false` is private state on `SessionService`, set once — organization selection, location
  selection and token rotation must not promote it (ADR-0111).
- **Organization switch carries nothing across.** Prove it.

## Read first

- `desktop/src/Qrafig.Desktop.Application/Navigation/NavigationModel.cs`
- `desktop/src/Qrafig.Desktop.Application/Context/` — `ClientContext`, `ClientContextService`
- `desktop/src/Qrafig.Desktop.Application/ViewModels/EmployeesViewModel.cs` and
  `CustomersViewModel.cs` — the most recent and most corrected patterns
- `desktop/src/Qrafig.Desktop/Views/EmployeesView.xaml` — the corrected XAML idioms
- `desktop/src/Qrafig.Desktop.Infrastructure/DesktopServices.cs`
- Tests: `NavigationTests`, `ClientContextTests`, `CompositionRootTests`, `MirroredContractTests`,
  `ShellStartupTests`, `SessionTests`, `RememberMeTests`, and the `*WorkspaceTests` for the nearest
  workspace
- `docs/client-save-policy.md`; ADRs 0109 – 0119, 0132, 0133, 0190, 0191, 0204

## Verification

Build; `desktop/tests/Qrafig.Desktop.Tests` including `NavigationTests`, `CompositionRootTests` and
`MirroredContractTests`; a vertical slice in `desktop/tests/Qrafig.Desktop.EndToEndTests` against the
real API; **and the live `QRAFIG.exe` smoke** — mandatory. See `qrafig-desktop-live-smoke`.

## Do not

- Do not compute a permission, price, discount ceiling or expected drawer on the client.
- Do not conflate the four access states, or reorder the checks.
- Do not render a blank page for an unbuilt module.
- Do not add a local table or queue to a module that is online-only by decision.
- Do not reference a UI framework from `Qrafig.Desktop.Application`.
- Do not patch a local row from a command response instead of re-reading.
- Do not autosave an ordinary form field by field.
- Do not add a mirrored code without adding it to the mirror test.

## Related skills

`qrafig-desktop-wpf` · `qrafig-desktop-live-smoke` · `qrafig-authorization` · `qrafig-offline-sync` ·
`qrafig-sqlite-local` · `qrafig-testing` · `qrafig-api-endpoints`.
