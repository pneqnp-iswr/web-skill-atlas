# QRAFIG skill registry

29 project skills at `.claude/skills/<name>/SKILL.md`, plus the bootstrap layer in `CLAUDE.md`.
Provenance and licences: [`sources.md`](sources.md). Routing evaluation set:
[`routing-eval.md`](routing-eval.md).

## How the system loads

| Layer | What | Cost |
| --- | --- | --- |
| **Always in context** | `CLAUDE.md` — source-of-truth order, the non-negotiables, the gate commands, the skill index, the conflict order | ~140 lines |
| **Entry point** | `/qrafig-router` — invoked (or model-selected) on essentially any QRAFIG task | one skill |
| **Near-always** | `qrafig-repo-state` (orientation), `qrafig-verification` (before reporting) | two skills |
| **On demand** | the remaining 26, selected by the router's lane table or by Claude from the descriptions | typically 2–5 per task |

A skill body loads only when the skill is used, so the reference material costs nothing until it is
needed. **Do not move skill content into `CLAUDE.md`** — that would put all of it in every prompt.

## The register

Legend — **O** = QRAFIG-original. All 29 are original; the *External* column names the canonical
sources the skill points at, referenced by URL and never vendored.

| # | Skill | Triggers on | Depends on / routes to | External referenced |
| --- | --- | --- | --- | --- |
| 1 | `qrafig-router` | any QRAFIG task; open-ended or multi-domain requests | every other skill | — |
| 2 | `qrafig-repo-state` | "continue", "what's next", "what's done", finding an ADR, doc-vs-code conflicts | router, architecture, verification | — |
| 3 | `qrafig-verification` | before reporting; "check before production"; choosing gates | testing, live-smoke, migrations, concurrency, tenancy | — |
| 4 | `qrafig-architecture` | crossing a layer, new module, released-contract change, writing an ADR | api-endpoints, migrations, concurrency, desktop-workspace | — |
| 5 | `qrafig-concurrency` | any read-modify-write, claim, counter, approval; "find race conditions" | postgres, testing, money, offline-sync, outbox | Trigger.dev race conditions & idempotency; claude-db concurrency audit |
| 6 | `qrafig-authorization` | any authorized route; roles, employees, POS eligibility, approvals | tenancy, appsec, pos-domain, offline-sync | Auth0 ASP.NET Core API authorization *(adapted)* |
| 7 | `qrafig-tenancy` | every new route, query, job, cache key, file path, export | authorization, api-endpoints, storage, reporting | claude-db multi-tenancy audit *(adapted)* |
| 8 | `qrafig-appsec` | credentials, tokens, hashes, signatures, secrets, PII, logs, advisories | authorization, tenancy, storage, observability | Auth0 application security review |
| 9 | `qrafig-testing` | writing or changing a test; suite selection; environmental failures | verification, concurrency, live-smoke, diagnostics | Testcontainers for .NET |
| 10 | `qrafig-observability` | telemetry, correlation, logging, redaction, queue health | outbox-jobs, appsec, diagnostics, performance | dotnet OpenTelemetry configuration |
| 11 | `qrafig-efcore-migrations` | entity, mapping, index, column, schema, "new migration" | postgres, concurrency, architecture, verification | dotnet EF Core query optimization; claude-db types & temporal audits |
| 12 | `qrafig-postgres` | locks, isolation, `SKIP LOCKED`, indexes, deadlocks, plans | concurrency, migrations, outbox-jobs, performance | Supabase Postgres *(adapted)*; keyset pagination; query plans |
| 13 | `qrafig-sqlite-local` | local database, operation queue, POS journal, local projections | offline-sync, pos-domain, desktop-workspace, testing | — |
| 14 | `qrafig-api-endpoints` | new route, contract, error code, validation, OpenAPI, idempotency, paging | tenancy, authorization, concurrency, observability | dotnet ASP.NET Core Web API; Minimal API OpenAPI |
| 15 | `qrafig-outbox-jobs` | integration events, handlers, webhooks, notifications, scheduled jobs | postgres, concurrency, observability, appsec | database queues & outbox *(adapted)*; hookdeck webhook patterns; idempotency |
| 16 | `qrafig-storage` | uploads, presigned URLs, quotas, orphaned objects, attachments | appsec, outbox-jobs, tenancy, migrations | Minimal API file upload *(adapted)* |
| 17 | `qrafig-money-finance` | any amount, balance, expense, transfer, approval, reconciliation | concurrency, pos-domain, reporting, purchasing | — |
| 18 | `qrafig-pos-domain` | sale, tender, shift, drawer, receipt, void, held cart, X/Z, return | offline-sync, money, authorization, inventory, desktop | — |
| 19 | `qrafig-offline-sync` | offline capture, replay, change feed, cursors, crash, reconnect | sqlite-local, pos-domain, authorization, concurrency | Trigger.dev idempotency |
| 20 | `qrafig-inventory` | movements, transfers, stocktakes, holds, opening inventory, cost | concurrency, postgres, purchasing, pos-domain | — |
| 21 | `qrafig-purchasing` | suppliers, purchase orders, receipts, landed cost, supplier debt | inventory, money, authorization, concurrency | — |
| 22 | `qrafig-customers-privacy` | customers, debt, loyalty, certificates, erasure, export, PII | appsec, tenancy, money, pos-domain | — |
| 23 | `qrafig-reporting` | reports, dashboards, aggregates, periods, drill-down | money, postgres, performance, tenancy | — |
| 24 | `qrafig-desktop-wpf` | any `.xaml`, view, style, converter, template, rendering defect | desktop-workspace, live-smoke, testing, performance | W3C keyboard interaction |
| 25 | `qrafig-desktop-live-smoke` | before claiming a Desktop change complete; run-time-only defects | desktop-wpf, desktop-workspace, verification | — |
| 26 | `qrafig-desktop-workspace` | new workspace or surface, navigation, access states, client context | desktop-wpf, live-smoke, authorization, offline-sync | — |
| 27 | `qrafig-site` | the marketing site — and nothing else loads with it | *(none — deliberately isolated)* | Vercel Next.js & React best practices; Cloudflare Workers; W3C keyboard |
| 28 | `qrafig-performance` | slow anything; capacity work | postgres, migrations, reporting, desktop-wpf, observability | dotnet performance analysis & trace collection; EF Core query optimization |
| 29 | `qrafig-diagnostics` | "something is broken", unexplained failures, incidents | testing, concurrency, desktop-wpf, offline-sync, observability | dotnet trace collection |

## Bundled tooling

| Path | What |
| --- | --- |
| `.claude/skills/qrafig-desktop-wpf/scripts/xaml_audit.py` | Static XAML audit: undefined `StaticResource` keys, wrong `TargetType`, `Trigger Property="Tag" Value="True"`, `DataContext` shadowing an un-rooted sibling binding, unstyled list controls, `TwoWay` without a path. Run from the repository root. A pre-filter for the live smoke, never a replacement. |

## Maintaining this system

- **Do not hard-code volatile state** in a skill — test counts, migration counts, the local schema
  version, the held-cart payload version. Say *"read it from `docs/implementation-status.md`"* instead.
  ADR numbers and titles are safe: the corpus is append-only.
- **When an ADR supersedes another**, update the skill that cites the old one.
- **When a module's claim closes**, `qrafig-repo-state` needs nothing new — it reads the ledger. But
  check that no skill states the module's status as a fact.
- **A new skill earns its place only if** it materially changes behaviour, prevents a plausible
  expensive bug, says what to inspect, carries concrete invariants, has a procedure and a verification,
  and does not duplicate another. If it can be replaced by "be careful and write good code", delete it.
- **Keep `CLAUDE.md` compact.** It is the only file loaded on every task.
- After changing the router or a description, re-run the cases in `routing-eval.md`.
