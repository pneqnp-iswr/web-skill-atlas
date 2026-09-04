---
name: qrafig-inventory
description: QRAFIG's stock rules — balance derived from append-only movements and never overwritten, two-step transfers because goods in transit belong to nobody, stocktakes whose expected quantities freeze at open, holds admitted by the same rules as movements, opening inventory as an additive elevated action, deterministic line ordering as the deadlock guard, server-owned cost valuation and cost confidentiality. Use for stock movements, transfers, stocktakes, corrections, write-offs, holds, opening inventory or anything that changes what is on a shelf.
when_to_use: Stock receive, write-off, correction, transfer, despatch, stocktake, count, adjustment, hold or reservation, opening inventory, on-hand versus available, cost price visibility.
---

# Inventory in QRAFIG

## The founding rule

**Inventory balance is derived, never overwritten** (ADR-0006). Every change is an append-only
`inventory_movements` row; `InventoryBalance` is a projection held so that listing stock does not sum
a ledger. A projection that two code paths can write will eventually disagree with the events that
justify it, and when it does there is no way to tell which is wrong.

A "correction" therefore means **the counted physical quantity**, unmistakably — it posts the movement
that makes the balance equal what somebody counted. It is not a direct write.

## Read first

- `backend/src/Qrafig.Application/Inventory/` — `StockLedger` and its services.
- `backend/src/Qrafig.Api/Endpoints/InventoryEndpoints.cs`.
- Desktop: `WarehouseViewModel`, `StockOperationViewModel`, `TransfersViewModel`,
  `TransferCreateViewModel`, `TransferActionViewModel`, `StocktakesViewModel`,
  `StocktakeRecordViewModel`, `OpeningInventoryViewModel`, and their views.
- Tests: `InventoryTests`, `InventoryConcurrencyTests`, `InventoryInvariantTests`,
  `InventoryEdgeCaseTests`, `InventoryCostConfidentialityTests`, `InventoryDirectOperationAuditTests`,
  `InventoryDiscoveryTests`, `TransferInvariantTests`, `TransferCommandAuditTests`,
  `StocktakeInvariantTests`, `StocktakeCommandAuditTests`, `OpeningInventoryTests`; Desktop
  `Warehouse*Tests` and the warehouse vertical slices.
- ADRs 0006, 0027, 0033, 0035 – 0038, 0138 – 0157.

## Deterministic line ordering is the deadlock guard (ADR-0037)

Two concurrent multi-product operations touching overlapping items take row locks on
`inventory_balances`. If one processes A then B and the other B then A, PostgreSQL deadlocks and kills
one. **`StockLedger` sorts every operation's lines by `product_id` before touching anything**, so all
callers acquire rows in the same sequence regardless of the order the client sent them.

Correctness under contention still comes from optimistic concurrency: balances carry `row_version`, so
two writers collide with `409 CONCURRENCY_CONFLICT` rather than one silently overwriting the other. A
**duplicate product within one operation is rejected** (`DUPLICATE_PRODUCT_LINE`), because the
resulting balance would otherwise depend on evaluation order.

`InventoryConcurrencyTests` proves this by observation: concurrent removals never oversell, concurrent
receipts never lose an update, opposing multi-product operations produce no server errors, concurrent
reservations never over-commit, and the ledger still sums to the balance afterwards.

## Transfers (ADR-0035, ADR-0038, ADR-0143 – ADR-0149)

**Two steps, because goods in transit belong to nobody.** Draft → reserved → despatched → in transit →
received; or cancelled before despatch.

- A **draft reserves and moves nothing**, and that is said in three places.
- A **short despatch leaves stock at the origin**; a **short receipt is a permanent loss**, shown per
  product before confirmation.
- **More cannot be despatched than was requested** (ADR-0144).
- **Warehouse sends no unit cost — the server values the movement** (ADR-0140); an internal transfer
  carries **server-owned cost** (ADR-0146). A client that could send cost could revalue stock through
  `inventory.manage`.
- Every command carries `Idempotency-Key`, and **the key belongs to the intent, not the attempt**
  (ADR-0141, ADR-0148). An outcome the key cannot settle is resolved by **asking the server**, never
  by guessing.
- The transfer **register is a query** and the released list is history (ADR-0147); the register walks
  a cursor to the end so unresolved work cannot be buried.
- **Online only** — no cache, no queue, no local table (ADR-0149).
- A document is re-read **authoritatively before and after every command**.

## Stocktakes (ADR-0036, ADR-0038, ADR-0150 – ADR-0157)

- **Expected quantities are frozen at open, not read at close.** A count compares against what was
  expected when counting started.
- A location may have **one *unresolved*** stocktake, not one *in progress* — a count awaiting
  approval is neither open nor finished, and its lines are already walked while its adjustments have
  not reached the ledger. Enforced by `ux_inventory_counts_open_per_store` on
  `(store_id) WHERE status IN ('InProgress','PendingApproval')` (ADR-0150).
- **"Count the shop" and "count these" are different questions** (ADR-0151).
- Approving takes ordinary inventory authority **and** the elevated capability (ADR-0152).
- **A counted line is not silently overwritten** (ADR-0153).
- A stocktake **movement window follows committed balance, not a pre-commit clock** (ADR-0157).
- Recording is the dangerous command, and its key belongs to the intent (ADR-0155).

## Holds and opening inventory

- **A hold is admitted by the same rules a movement is** (ADR-0145). On-hand, held and available stay
  **distinct** everywhere.
- **Opening inventory is additive, and the key is what protects it** (ADR-0156). It is an elevated
  action.

## Cost confidentiality

**Cost price is withheld, not merely hidden** (ADR-0033) — the field does not travel to a caller
without the capability. It is withheld **at the projection, on every route that carries it**
(ADR-0143), and cost, margin and valuation obey the catalog's visibility rule (ADR-0073). Building the
Warehouse transfer surface repaired six contract defects, two of them cost leaks.

The stock desk **finds its own products, and nothing priced travels with them** (ADR-0138).

## One location entity (ADR-0027)

There are no separate store and warehouse entities — one location entity with a management contract
that is **not its identity** (ADR-0139).

## Verification

Backend integration including the concurrency and invariant suites; a race test for any new
balance-affecting path; a cost-confidentiality assertion on any route that could carry cost; Desktop
warehouse tests and the vertical slices; **and a live `QRAFIG.exe` smoke** for a Warehouse UI change.
Assert the ledger still sums to the balance after any concurrent scenario.

## Do not

- Do not write a balance directly.
- Do not accept a client-supplied unit cost for an internal movement.
- Do not let a duplicate product line into one operation.
- Do not sort lines anywhere but the shared entry point.
- Do not read expected quantities at close.
- Do not allow a second unresolved stocktake at a location.
- Do not queue a transfer or a stock mutation offline.
- Do not overwrite a counted line silently.
- Do not add a cost field to a projection without checking every route that reads it.

## Related skills

`qrafig-concurrency` · `qrafig-postgres` · `qrafig-purchasing` (receipts feed stock) ·
`qrafig-pos-domain` (a sale's stock consequence) · `qrafig-money-finance` (valuation) ·
`qrafig-desktop-workspace` · `qrafig-efcore-migrations`.
