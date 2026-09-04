---
name: qrafig-pos-domain
description: QRAFIG's point-of-sale semantics — a shift is accountability for cash rather than a session, a sale is a snapshot never refused for being late, tenders and exact settlement, voids recorded beside a sale rather than editing it, drawer cash in and out, held carts as a claim that must survive a lost answer, X and Z reports, returns and manager approval, and the sequence and document numbering rules. Use for any till behaviour, sale, shift, drawer, receipt, void, held cart, report or return change.
when_to_use: Sale, tender, shift open or close, cash drawer, receipt, reprint, void, parked or held cart, X/Z report, return or refund at the till, cashier or manager authorization at a till.
---

# The POS domain

## Read first

- `README.md` §§ *The till*, *Taking goods back*, *The supervisor's screen*, *Parked carts*,
  *The cash drawer*, *Shift reports — X and Z*, *POS authority*, *Shift accounting after a close*.
- `backend/src/Qrafig.Application/Sales/` — `SaleService`, `ShiftService`, `CartService`,
  `DocumentNumbers`, `PosEligibility`, `PosCapabilities`, `ShiftReconciliation`,
  `HeldCartPayloadLimits`, `SaleSyncHandlers`.
- `backend/src/Qrafig.Application/Returns/`, `backend/src/Qrafig.Api/Endpoints/PosSalesEndpoints.cs`,
  `ReturnEndpoints.cs`.
- Desktop: `PosTillViewModel`, `PosShiftReportViewModel`, `PosCashViewModel`, `PosHeldCartsViewModel`,
  `PosReturnViewModel`, `PosSupervisorViewModel`, and their views.
- Tests: `SalesTests`, `ReturnTests`, `HeldCartTests`, `PosShiftReportTests`,
  `ShiftReconciliationTests`, `PosAuthorityTests`, `OfflineSalesTests`; Desktop `Pos*Tests`.
- ADRs 0049 – 0063, 0116, 0120 – 0130, 0134 – 0137.

## Shift

**A shift is accountability for cash, not a session** (ADR-0049). Its closing figures —
`expectedCashMinor`, `countedCashMinor`, `discrepancyMinor` — are **historical evidence**: what was
known and what was counted at that moment. Nothing rewrites them.

Records feeding that arithmetic still arrive afterwards (a sale rung during an outage, a refund a
manager finally agrees, a void, a paid-in). Each becomes **one append-only row** in
`shift_accounting_adjustments`, deduplicated by the **business effect** that caused it, written in the
same transaction (ADR-0127). The API reports them **additively**, so no existing field changes meaning:

```
expectedCashMinor                 frozen at close, unchanged forever
countedCashMinor                  what was physically counted
discrepancyMinor                  counted − expected, as recorded at the time
lateDrawerAdjustmentMinor         everything that arrived afterwards, signed
postClosePhysicalAdjustmentMinor  the part that moved after the count
reconciledExpectedCashMinor       expected + lateDrawerAdjustment
reconciledDiscrepancyMinor        counted − what the drawer is now known to have held at the count
```

**Physical cash is never counted twice.** The close banks the whole counted drawer, so activity already
in the drawer when it was counted corrects only the *expectation* and posts nothing. Only money that
demonstrably moved **after** the count reaches the cash account, as one immutable `ShiftLateActivity`
entry through `FinanceLedger`.

**Close and drawer work are serialized per shift** by a transaction-scoped advisory lock that every
participant takes — sale, cash in, cash out, void, return posting, approval, close and force-close — so
two requests can never both read "open" and both commit (ADR-0128).

**A shift read is one moment, not six** — every shift read runs over one `REPEATABLE READ` snapshot
(ADR-0136). That is what an X report is built on.

One open shift per device is enforced by a **partial unique index** on both sides, server and local.

## Sale

- **A sale is a snapshot** of prices, names and tax as they were, **and is never refused for being
  late** (ADR-0050). A sale synchronized days later still lands.
- **Payments must sum to exactly the total.** `SaleService` refuses anything else, so the amount that
  travels is what settled the sale. **Change is not an overpayment**: what the drawer gave back is
  kept locally and printed. Modelling it the other way sends a payment row the server rejects, after
  the customer has taken their change and gone (ADR-0116).
- **Tax is carried as numbers, not as a country's rules** (ADR-0051).
- **Sales get a real sequence, not a row count** (ADR-0053), and carry their query-path indexes from
  the start (ADR-0055, ADR-0075).
- A sale **points at its customer and never snapshots their name** (ADR-0184).
- `sale.completed` carries the customer, and **only** the customer (ADR-0178).

## Void, not edit

**A void is a fact recorded beside a sale, never an edit of one** (ADR-0124). The sale remains. The
same shape applies everywhere: corrections are new records.

## Cash in and out

Cash in and out are **drawer facts**, and **the expected drawer stays the server's** (ADR-0125). Both
reach the server with their reasons and their cashier intact.

## Held (parked) carts

**A held cart is not a sale** (ADR-0052). It is the **shop's**, not the till's, and **picking one up is
a claim that must survive a lost answer** (ADR-0134) — resuming *settles* it, so a till that claimed
first and then found it could not read the payload would have taken the work out of every other
counter's reach and thrown it away.

The payload format is declared **beside** the blob (`payload_schema`, `payload_version`) rather than
parsed out of it, so the server interprets nothing and a list of two hundred carts is not two hundred
JSON parses. Defaults read as **undeclared** rather than pretending to be a version: a cart parked
before the contract existed is correctly refused for resume and offered for discard. Read the current
`qrafig.pos.cart` version from the status ledger.

A held cart **may carry an identity, never an authority** (ADR-0186).

## X and Z

**X is a read; Z is a document about a close that already happened** — and both are core POS
(ADR-0135). A shift closed during an outage produces **no Z until QRAFIG has the close**. The server's
answer about a shift is **written down** so the Z survives the printer (ADR-0137). There is **no Z
counter and no Z sequence**.

## Returns

- **The return reason decides the outcome, so it is a catalog** (ADR-0057), which rides the change feed;
  retirement is a flag, not a deletion (ADR-0130). A till cannot fetch its own return reasons, so the
  snapshot carries them (ADR-0121).
- **A return that needs approval moves nothing until it is approved** (ADR-0058).
- **A return without a receipt is bounded by who, not by what** (ADR-0059).
- **A return unwinds what the sale took, not what the refund gives** (ADR-0061).
- **A return is a second durable capture, not a sale with the sign flipped** (ADR-0120).
- **A manager authorizes one decision, and never takes the till** (ADR-0123).
- Credit, points and gift certificates are **tenders, not exceptions** (ADR-0060). A till is told what
  a tender does and refuses the three it cannot verify (ADR-0187); a gift certificate is spent **by
  code**, so the till has to ask for one (ADR-0189).

## Document numbers

Claimed under a lock, one statement, per tenant. Prefixes are distinct across domains (`FT-` for money
transfers because `TR-` was taken by stock transfers).

## The two authorities

Fresh online commands go through `CurrentPosAuthority`; synchronized operations go through
`PosActorResolver` and deliberately check none of it. See `qrafig-authorization` — this distinction is
the one most likely to be broken by a well-meaning change.

## Verification

Backend integration (`SalesTests`, `ReturnTests`, `HeldCartTests`, `PosShiftReportTests`,
`ShiftReconciliationTests`, `OfflineSalesTests`); Desktop view-model `Pos*Tests`; Desktop end-to-end
`PosCheckoutVerticalSliceTests`, `PosHeldCartVerticalSliceTests`,
`PosShiftReportVerticalSliceTests`, `BackofficeReturnApprovalTests`; **and a live `QRAFIG.exe` smoke**
for any till UI change. Add a concurrency test for anything touching a shift, a drawer or a held cart.

## Do not

- Do not edit a completed sale; record a void, a return or an adjustment.
- Do not rewrite a closed shift's figures; report additively.
- Do not post a cash sale to the money account when it rings.
- Do not send change as a payment.
- Do not refuse a synchronized sale because it is late or its cashier is no longer active.
- Do not let a manager's approval take over the till.
- Do not let the client decide a discount ceiling, a permission or an expected drawer.
- Do not parse a held-cart payload on the server to decide compatibility.

## Related skills

`qrafig-offline-sync` · `qrafig-money-finance` · `qrafig-authorization` · `qrafig-inventory`
(a sale's stock consequence) · `qrafig-customers-privacy` (customer on a sale) ·
`qrafig-desktop-workspace` · `qrafig-desktop-live-smoke` · `qrafig-concurrency`.
