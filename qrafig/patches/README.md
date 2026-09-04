# Pending changes for the QRAFIG repository

These patches are **work for `pneqnp-iswr/qrafig`, not for this repository.** They live here because
the session that produced them had read-only access to QRAFIG and could only push to this branch.
Applying one is a normal `git am`; nothing here is part of the skill pack.

```bash
cd /path/to/qrafig
git checkout -b claude/xaml-contract-tests
git am /path/to/web-skill-atlas/qrafig/patches/<file>.patch
```

| Patch | What it does | Verified |
| --- | --- | --- |
| `qrafig-xaml-contract-tests.patch` | Makes the static XAML audits executable as `XamlContractTests` in `Qrafig.Desktop.Tests`, and fixes the six defects they find: the never-matching `Trigger Property="Tag"` tab strip in `CustomersView`, `FinanceView`, `PurchasingView` and `WarehouseView` (27 buttons), and a detail card's `Visibility` shadowed by a `DataContext` override in `StocktakesView` and `TransfersView`. Adds the decision record and updates the status ledger. | On Linux: solution build and `desktop/src/Qrafig.Desktop` build 0 warnings / 0 errors; `Qrafig.UnitTests` 59/59; `Qrafig.Desktop.Tests` 1068 total / 1059 passing, the 9 failures being the unchanged DPAPI platform baseline; `has-pending-model-changes` clean; no vulnerable packages. **Not run:** the two Docker-backed suites and the live `QRAFIG.exe` smoke — neither covers this change, and the ledger update says so. |

Once a patch is applied and pushed, delete it from here.
