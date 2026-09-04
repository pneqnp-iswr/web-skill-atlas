---
name: qrafig-purchasing
description: QRAFIG's procurement rules — a purchase order states intent while receipts state fact, receiving as one idempotent unit of work, landed cost finalized exactly once before the first receipt, supplier debt derived from documents and never stored, damaged quantity consuming the order without entering sellable stock, receipt-linked returns valued from the immutable receipt, and spend approval as an authority separate from drafting. Use for suppliers, purchase orders, goods receipts, supplier invoices, payments and supplier returns.
when_to_use: Suppliers, purchase orders, approving spend, goods receipt, partial or damaged receipt, landed cost, supplier invoices and payments, supplier returns, supplier debt.
---

# Purchasing in QRAFIG

## The founding distinction

**A purchase order states intent; receipts state fact** (ADR-0039). A draft commits to nothing and
moves no stock. Nothing about an order changes inventory until a goods receipt says something arrived.

**Supplier debt is derived, never stored** (ADR-0040) — the same rule as stock and money balances.

## Read first

- `backend/src/Qrafig.Application/Purchasing/`, `backend/src/Qrafig.Api/Endpoints/PurchasingEndpoints.cs`,
  `backend/src/Qrafig.Api/Idempotency/PurchasingReplay.cs`.
- Desktop: `PurchasingViewModel`, `PurchasingOrdersViewModel`, `PurchasingSuppliersViewModel`,
  `PurchasingDocumentsViewModel`, `PurchasingView.xaml`.
- Tests: `PurchasingTests`, `PurchasingConcurrencyTests`, `PurchasingAuthorizationTests`;
  Desktop `PurchasingServiceTests`, `PurchasingViewModelTests`, `PurchasingVerticalSliceTests`.
- ADRs 0039 – 0041, 0158 – 0168.

## The rules

| | |
| --- | --- |
| **Authority composes** | Purchasing authority composes an inventory operation with financial control (ADR-0158). **Drafting and approving spend are different authorities.** Cancellation and close-short are different claims. |
| **Receiving is one unit of work** | idempotent by key (ADR-0041). Partial receipts are normal. |
| **Damage** | damaged quantity **consumes the order** but **never enters sellable stock**. |
| **Landed cost** | finalized **exactly once, before the first receipt**, and refused afterwards rather than revaluing stock already priced (ADR-0161, ADR-0166). Finalization is a **recorded fact**, not one inferred from a row version — inference got this wrong once, because `ApplyReceipt` advances the same counter. |
| **Invoices** | a cursor-complete outstanding queue. Payments **cannot overpay, over-settle under contention, or debit a Finance account twice**. |
| **Supplier returns** | record **physical shipment, not an unearned supplier credit** (ADR-0163); valued from the **immutable receipt** and bounded by what it has left (ADR-0167 publishes that returnable bound). |
| **Confidentiality** | purchasing cost and supplier debt are **two independent confidential projections** (ADR-0159). Check both on every route. |
| **Numbers and queues** | document numbers and operational queues use the proven tenant patterns (ADR-0160). |
| **Idempotency** | **one stable intent key** resolves uncertain outcomes (ADR-0162). A supplier save names the **card version** the operator actually edited (ADR-0164). |
| **Desktop** | a tenant-bound **online composition**, not a second domain (ADR-0165). No local table, no queue. |
| **Validation** | a validator may not dereference the field it has just rejected (ADR-0168). |

## Not built, deliberately

Supplier credit notes and refund settlement, OCR invoice capture, supplier EDI, automatic reorder
suggestions, a supplier portal, mobile receiving, batch/expiry purchasing. Check the ledger's
completion criteria before assuming any of these exist.

## Verification

Backend integration including `PurchasingConcurrencyTests` and `PurchasingAuthorizationTests`; a race
test for any new claim (a receipt, a payment, a landed-cost finalization); a confidentiality assertion
on any route that could carry cost or supplier debt; Desktop tests and the vertical slice; **and a
live `QRAFIG.exe` smoke** for a Purchasing UI change.

## Do not

- Do not move stock from an order.
- Do not store supplier debt.
- Do not let damaged quantity reach sellable stock.
- Do not allow landed cost to be re-finalized after a receipt.
- Do not infer finalization from a row version.
- Do not let a payment overpay or double-debit under contention.
- Do not treat a supplier return as a credit.
- Do not queue a purchasing command offline.

## Related skills

`qrafig-inventory` · `qrafig-money-finance` · `qrafig-authorization` · `qrafig-concurrency` ·
`qrafig-desktop-workspace`.
