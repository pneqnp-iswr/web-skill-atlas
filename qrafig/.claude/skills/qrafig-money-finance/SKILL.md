---
name: qrafig-money-finance
description: Get QRAFIG's money right — integer minor units with checked arithmetic that refuses rather than wraps, never summing two currencies, an append-only ledger whose balance is a projection, cash reaching the ledger at shift close rather than at each sale, expenses that move nothing until approved, cross-currency transfers with no invented rate, reconciliation as two separate decisions, and what is mutable versus what is historical evidence. Use for any change to money, balances, accounts, expenses, transfers, approvals or reconciliation.
when_to_use: Money accounts, ledgers, balances, expenses, income, approvals, transfers, reconciliation, daily cash, supplier or customer obligations, currency handling, any amount field.
---

# Money and finance in QRAFIG

## The two mistakes a money module makes, and QRAFIG's answers

1. **Arithmetic that lies.** `bigint` is the right storage — exact unlike a float, cheap unlike
   `numeric` — but C# `long` wraps, so `BalanceMinor += signedAmountMinor` turns a large balance
   negative with no error anywhere. And `Math.Abs(long.MinValue)` throws, from a figure a client can
   simply send as an opening balance.
2. **Adding units that have no common total.** A manat safe and a dollar account do not sum. QRAFIG
   owns **no exchange-rate table** and will not derive one.

## The rules

| | |
| --- | --- |
| Storage | `bigint` **minor units** beside an explicit ISO 4217 code. Never `float`, `double` or `decimal` for money. |
| Arithmetic | **`MoneyArithmetic` is the only way money is combined.** Every operation is `checked`; a figure that will not fit is refused with `MONEY_AMOUNT_OUT_OF_RANGE`. Nothing rounds, saturates or clamps. |
| Ceiling | A single request may state at most `MoneyArithmetic.MaxAbsoluteMinor` = `long.MaxValue / 1000`, so a thousand maximal postings still accumulate inside the range their projection is held in. |
| Exception | `MoneyOverflowException : InvalidOperationException`, so domain guards that already translate that family keep working. An `OverflowException` reaching the middleware is a **defect** and answers 500; this is a **business refusal** and answers a stable conflict. |
| Currencies | **Nothing is ever summed across currencies.** Movements and balances are grouped by the entry's own currency and the API returns a **list keyed by currency**. The absence of a combined figure is **stated on screen**, not left as an apparent omission. |
| The exception | Only the three obligation figures are single — customer debt, supplier debt and gift-certificate liability — because sales, invoices and certificates are all denominated in the base currency by construction. |
| Reports | A read whose aggregate will not fit answers a **stated refusal**, rather than letting `Enumerable.Sum`'s `OverflowException` reach the middleware as a 500. |

An organization has one base currency; every location inherits it and may not be given another
(ADR-0028). A money account may hold any currency the business banks in.

## Ledger and projection

`finance_entries` is **append-only and is the truth**. Every movement — a shift banking its takings, an
approved expense, a transfer, a supplier being paid — is one row carrying its direction, its amount,
its cause and the balance that followed it.

`money_accounts.balance_minor` is a **projection**: moved only by `FinanceLedger.PostAsync`, never set.
It exists so that listing twenty accounts does not sum twenty ledgers.

**What keeps a projection honest is checking it.** Reconciliation recomputes the balance from the
entries and **refuses to proceed** if they disagree, with `LEDGER_OUT_OF_BALANCE` — that is a defect,
not a counting error, and recording a difference against a broken projection would invent a
discrepancy that is not real.

An account **may go negative**. A shop whose opening balance was never entered still has to open a
till; blocking the first shift of the day over bookkeeping would be worse.

## Cash reaches the ledger at close, not at each sale (ADR-0066)

While a shift is open, its money is in a drawer, not in an account. The account is touched exactly
twice — `shift_float` out when the shift opens, `shift_takings` in when it closes — plus
`cash_discrepancy` **as its own line** when the count differs, because a shortfall absorbed into the
takings is a shortfall nobody sees.

So: an open till's takings are visible on the **shift** and not yet in the account, and the daily cash
summary reads shift figures **from the shifts**. Reading them from the ledger would report zero for a
till that has been selling all day.

The location's cash account is created lazily on first shift open, protected by
`ux_money_accounts_store_default` on `(store_id) WHERE is_default_for_store`.

## What is mutable and what is historical evidence

| Historical evidence — never rewritten | Mutable / recomputed |
| --- | --- |
| A completed sale, a financial document, a ledger entry | An account's balance projection |
| A closed shift's `expectedCashMinor`, `countedCashMinor`, `discrepancyMinor` | The *reconciled* figures reported **additively** beside them |
| The rendered text of a notification | A category catalog, an approval threshold |
| A decision already taken under an old threshold | The threshold itself |

Changing the approval threshold leaves decisions already taken alone. A backdated entry is **appended
now and reported in the period it happened in**. A day the clocks change on is 23 or 25 hours long,
not 24.

## Semantics that are decisions, not arithmetic

- A **supplier invoice is debt**; its **payment is cash flow**; **neither is an expense**.
- An **internal transfer** changes where the money is, not how much there is (ADR-0068). A
  cross-currency transfer records **what was sent and what arrived**, both stated by the operator —
  QRAFIG invents no rate.
- An **expense awaiting approval has moved no money** and says so (ADR-0067). A refusal requires a
  reason and posts nothing.
- **Reconciliation is two decisions**: recording a count corrects nothing; the correction is a second,
  separate act (ADR-0199). A balanced reconciliation has its own stable state.
- **Money is posted where it demonstrably went, and nowhere else** (ADR-0070).
- **Revenue, gross profit, expenses, cash flow and balances are five numbers** (ADR-0069), kept apart.
  Gross profit is labelled as saying nothing about overheads; **net profit is not computed**.
- A money transfer's document prefix is `FT-`, because `TR-` was already taken by stock transfers.
- Finance Backoffice is **online only**, with no cache, no local table and no queue (ADR-0203).

## Concurrency

Money is contended by construction. See `qrafig-concurrency`; the Finance-specific rules:

- **A balance is serialized by its account** (ADR-0194) — two lawful postings queue, they do not
  conflict.
- **The lock order is global, fixed and ascending by id** (ADR-0196): the calling domain's scope
  (drawer, customer, certificate), then the record being decided about, then one section per account
  ascending by id, then the document-number gate. `FinanceLedger.WithAccountsAsync` sorts the pair so a
  caller cannot get it wrong.
- A **lazily created account is claimed inside the caller's transaction** (ADR-0195).
- A **code is claimed inside the section that inserts it**, and **a save names the version it was
  composed against** (ADR-0197).
- **An approval decision is serialized by the record it is about** (ADR-0198) — two approvers post one
  expense once, and approve racing reject settles once.
- A **shared customer balance is serialized by its subject, not by the drawer** (ADR-0173).

## Read first

- `backend/src/Qrafig.Domain/Common/MoneyArithmetic.cs`
- `backend/src/Qrafig.Application/Finance/` — `FinanceLedger`, `FinanceLocks`, `FinanceRecordService`,
  `FinanceTransferService`, `MoneyAccountService`, `FinanceReportService`
- Tests: `MoneyArithmeticTests`, `MoneyTests` (unit); `FinanceConcurrencyTests`,
  `FinanceInvariantTests`, `FinanceTests` (integration); `FinanceWorkspaceTests` (Desktop)
- ADRs 0004, 0007, 0028, 0040, 0065 – 0074, 0193 – 0203.

## Verification

Unit boundary tests including `long.MinValue`, `long.MaxValue` and the released ceiling; a second
currency; concurrent postings to one account; two approvers on one expense; opposite transfers
queueing rather than deadlocking; a backdated entry reported in its own period; a DST day; and the
client contract — balances shown **per currency and never as one figure**, a save naming its version,
a lost answer replayed under the **same** key rather than re-composed.

## Do not

- Do not add money outside `MoneyArithmetic`.
- Do not introduce `decimal`, `float` or `double` for a monetary amount.
- Do not sum across currencies, or invent a rate.
- Do not set `balance_minor` directly.
- Do not post to an account while a shift is open.
- Do not rewrite a closed shift's frozen figures; report additively.
- Do not clamp or saturate an out-of-range figure.
- Do not compute net profit or present gross profit as if it were.
- Do not cache Finance data locally on the client.

## Related skills

`qrafig-concurrency` · `qrafig-pos-domain` (shift and drawer) · `qrafig-reporting` ·
`qrafig-purchasing` · `qrafig-customers-privacy` (debt, loyalty, certificates) · `qrafig-postgres`.
