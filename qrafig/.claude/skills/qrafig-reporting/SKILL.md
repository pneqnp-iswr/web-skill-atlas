---
name: qrafig-reporting
description: Build QRAFIG's business-wide figures correctly — reports recomputed from documents with nothing pre-aggregated, one consistent moment per report rather than six, five numbers kept apart, per-currency figures with no invented total, a business day belonging to the location that worked it, cost and margin obeying the catalog's visibility rule, bounded synchronous reads that refuse rather than truncate, and the dashboard composed from the reports. Use for any report, dashboard, aggregate, export of figures or period calculation.
when_to_use: Reports, dashboards, KPIs, aggregates, revenue, gross profit, cash flow, period and date-range calculations, drill-down, export of figures, the Reports workspace.
---

# Reporting in QRAFIG

## The rules

| | |
| --- | --- |
| **Recompute** | **A report recomputes from documents; nothing is pre-aggregated** (ADR-0071). No summary tables, no materialized rollups, no counter columns. The reporting phase added **indexes only**, which is what a phase that pre-aggregates nothing looks like. |
| **One moment** | **A report is one moment, not six** (ADR-0136). Assemble it over a single `REPEATABLE READ` snapshot — no lock, read-only, so the next customer never waits behind a report and it can never fail to serialize. Several statements at read-committed produce figures that are each defensible and impossible together. |
| **Five numbers** | **Revenue, gross profit, expenses, cash flow and balances are five numbers** (ADR-0069) and are kept apart. Gross profit is labelled as saying nothing about overheads. **Net profit is not computed.** |
| **Currency** | Figures are returned **keyed by currency**. Nothing is summed across currencies, and the absence of a combined total is **stated** rather than left as an omission. Only customer debt, supplier debt and gift-certificate liability are single figures, being denominated in the base currency by construction. |
| **Business day** | **A business day belongs to the location that worked it** (ADR-0072). Use the location's timezone, not the server's and not the caller's. A day the clocks change on is 23 or 25 hours long. |
| **Cost** | Cost, margin and valuation obey the catalog's visibility rule (ADR-0073). A caller without the capability does not receive the field. |
| **Bounded** | **A synchronous report is bounded, and says what to do about it** (ADR-0074). Count before loading and refuse with a named code; do not truncate. An aggregate that will not fit answers a stated refusal rather than letting an `OverflowException` reach the middleware as a 500. |
| **Scope** | A store-scoped figure **says which figures are not the store's**. |
| **Dashboard** | **The dashboard is composed from the reports, not from its own queries** (ADR-0076) — one definition of revenue, not two. |
| **Cash** | The daily cash summary reads shift figures **from the shifts**; reading them from the ledger would report zero for a till that has been selling all day (ADR-0066). |
| **Backdating** | A backdated entry is appended **now** and reported in the period it **happened** in. |

## Pagination traps

- An **operational queue** must be cursor-complete — it walks to the end so unresolved work cannot be
  buried. A **history** list may be capped (ADR-0200). Getting these the wrong way round is a real
  defect: an unresolved-difference queue capped like history hides work.
- Do **not** compute a total by paging and summing on the caller's side; that produces a figure from
  several snapshots.
- Cursors must not be replayable across tenants.

## The Reports workspace

At the time of writing, Reports is the **named next Desktop slice and is not built**. It is
feature-gated (`reports`) and **not part of the trial plan**, so the first honest question the slice
must answer is **what a locked module shows** — see `LockedModuleView.xaml` and the four access states
in `qrafig-desktop-workspace`.

Two promises already made that Reports has to keep:

1. Finance computes gross profit and labels it as saying nothing about overheads (ADR-0193).
2. The Customers and Finance overviews describe the page that is loaded rather than the business,
   using the sentence *"Reports computes business-wide figures from the documents themselves"*.

Check `docs/implementation-status.md` for the current state before assuming any of this has changed.

## Read first

- `backend/src/Qrafig.Application/Reporting/`, `backend/src/Qrafig.Api/Endpoints/ReportEndpoints.cs`.
- `backend/src/Qrafig.Application/Finance/FinanceReportService.cs`.
- Tests: `ReportingTests`, `FinanceInvariantTests` (period and DST semantics), `PosShiftReportTests`.
- ADRs 0066, 0069 – 0076, 0136, 0193, 0200.

## Verification

Prove: the same figure computed two ways agrees; a report spanning a concurrent commit sees the state
either **before** it or **after** it, never half of each; two currencies produce two figures and no
total; a DST day is 23 or 25 hours; a backdated document lands in its own period; a caller without the
cost capability receives no cost; a too-large read refuses with its code; and a cross-tenant call
returns nothing of the neighbour's. Add a performance measurement for any new aggregate.

## Do not

- Do not add a summary table, a rollup or a counter column.
- Do not assemble a report from several independent snapshots.
- Do not sum across currencies or invent a rate.
- Do not use the server's timezone for a business day.
- Do not truncate a bounded read.
- Do not give the dashboard its own queries.
- Do not read an open shift's takings from the ledger.
- Do not leak cost through a report projection.

## Related skills

`qrafig-money-finance` · `qrafig-postgres` (snapshots, indexes, plans) · `qrafig-performance` ·
`qrafig-tenancy` · `qrafig-api-endpoints` · `qrafig-desktop-workspace`.
