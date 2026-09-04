# Source manifest — the QRAFIG skill system

Every part of the skill system, where it came from, and under what terms.

**No external skill file is vendored into this repository.** Reused and adapted material is
**referenced by canonical URL** and re-expressed as original QRAFIG procedure. That keeps provenance
honest, keeps the pack small, and avoids redistributing anyone's text under terms this repository
cannot grant. Where an external skill is listed as *reused*, the QRAFIG skill names it and says when to
read it; where it is *adapted*, the QRAFIG skill states the constraint or override QRAFIG applies on
top of it.

Licences below are as published by the upstream repository at the time of research (2026-09-04).
**Re-check the upstream LICENSE before copying any text**, and never infer a licence.

---

## 1. QRAFIG-original skills (29)

Type: `qrafig-original`. Source: this repository — `README.md`, `docs/architecture-decisions.md`,
`docs/implementation-status.md`, `docs/api-roadmap.md`, `docs/client-save-policy.md`, and the
implementation and tests themselves. Licence: same as the QRAFIG repository.

| Skill | Why a generic skill could not do this |
| --- | --- |
| `qrafig-router` | Routing over QRAFIG's own module map, ADR corpus and gate matrix |
| `qrafig-repo-state` | Navigating a 3 600-line ledger and a 200-plus ADR corpus, and recognising a closed claim |
| `qrafig-verification` | QRAFIG's gate matrix, the run-suites-separately trap, the platform gaps |
| `qrafig-architecture` | The five-project topology, the append-only ADR convention, released-contract rules |
| `qrafig-concurrency` | QRAFIG's own race catalogue, lock orders and independent-client test idiom |
| `qrafig-authorization` | Current authority vs historical attribution — a distinction generic advice inverts |
| `qrafig-tenancy` | The single `OrganizationContext` choke point and 404-over-403 |
| `qrafig-appsec` | ES256 offline entitlement, PIN verifiers shipped to the till, DPAPI blobs |
| `qrafig-testing` | Four suites with different powers, and a documented class of defect none can catch |
| `qrafig-observability` | The correlation contract, the outbox meter, `job_runs`, redaction rules |
| `qrafig-efcore-migrations` | Append-only migrations, refuse-rather-than-repair `Up`, populated-database proof |
| `qrafig-postgres` | The specific isolation, advisory-lock and partial-index decisions QRAFIG rests on |
| `qrafig-sqlite-local` | `user_version` chain, `BEGIN IMMEDIATE`, durability-before-success, per-device keys |
| `qrafig-api-endpoints` | The error-code contract, idempotency semantics, load-bearing middleware order |
| `qrafig-outbox-jobs` | What QRAFIG's outbox does and explicitly does **not** promise |
| `qrafig-storage` | Reserve-before-bytes, measured checksums, the three passes |
| `qrafig-money-finance` | `MoneyArithmetic`, the no-cross-currency rule, ledger-vs-projection |
| `qrafig-pos-domain` | Shift, drawer, void, held cart, X/Z semantics as QRAFIG defines them |
| `qrafig-offline-sync` | An operation-log, server-authoritative model — the opposite of CRDT advice |
| `qrafig-inventory` | Derived balance, two-step transfers, frozen stocktake expectations |
| `qrafig-purchasing` | Intent vs fact, landed cost once, derived supplier debt |
| `qrafig-customers-privacy` | Anonymization-not-deletion, the bounded export, bearer certificates |
| `qrafig-reporting` | Recompute-from-documents, one snapshot, five numbers, business day |
| `qrafig-desktop-wpf` | An empirically derived WPF defect catalogue plus a working static audit |
| `qrafig-desktop-live-smoke` | A gate no generic skill defines, in a form that produces evidence |
| `qrafig-desktop-workspace` | Four access states, mirrored contracts, client-renders-decisions |
| `qrafig-site` | The site's own divergences, dictionaries, tokens and content truth check |
| `qrafig-performance` | Which optimizations QRAFIG's decisions forbid |
| `qrafig-diagnostics` | Triage across four surfaces with QRAFIG's own failure taxonomy |

Bundled tool: `.claude/skills/qrafig-desktop-wpf/scripts/xaml_audit.py` — original, written for this
repository, and run against it during authoring.

---

## 2. External skills referenced (reuse / adapt)

Loaded by a person or by Claude **when the QRAFIG skill points at them**. None is required for QRAFIG
to work; each adds framework-level depth QRAFIG's own skills deliberately do not restate.

| Skill | Source | Author / org | Licence | Type | Used by | Why selected |
| --- | --- | --- | --- | --- | --- | --- |
| ASP.NET Core Web API Engineering | https://github.com/dotnet/skills/blob/main/plugins/dotnet-aspnetcore/skills/dotnet-webapi/SKILL.md | `dotnet` (Microsoft) | MIT | reused | `qrafig-api-endpoints` | Official .NET skill repository; current-generation ASP.NET Core guidance from the framework owner |
| Minimal API OpenAPI | https://github.com/github/awesome-copilot/blob/main/skills/aspnet-minimal-api-openapi/SKILL.md | `github` | MIT | reused | `qrafig-api-endpoints` | Minimal-API OpenAPI specifics; QRAFIG uses minimal APIs with per-operation schemas |
| Optimizing EF Core Queries | https://github.com/dotnet/skills/blob/main/plugins/dotnet-data/skills/optimizing-ef-core-queries/SKILL.md | `dotnet` (Microsoft) | MIT | reused | `qrafig-efcore-migrations`, `qrafig-performance` | Official; query-shape and tracking guidance QRAFIG's skills do not restate |
| ASP.NET Core OpenTelemetry Configuration | https://github.com/dotnet/skills/blob/main/plugins/dotnet-aspnetcore/skills/configuring-opentelemetry-dotnet/SKILL.md | `dotnet` (Microsoft) | MIT | reused | `qrafig-observability` | Official; matches the repository's OpenTelemetry packages |
| .NET Performance Analysis | https://github.com/dotnet/skills/blob/main/plugins/dotnet-diag/skills/analyzing-dotnet-performance/SKILL.md | `dotnet` (Microsoft) | MIT | reused | `qrafig-performance` | Official diagnostics procedure |
| .NET Production Trace Collection | https://github.com/dotnet/skills/blob/main/plugins/dotnet-diag/skills/dotnet-trace-collect/SKILL.md | `dotnet` (Microsoft) | MIT | reused | `qrafig-performance`, `qrafig-diagnostics` | Official; how to capture a trace from a running process |
| Minimal API File Upload | https://github.com/dotnet/skills/blob/main/plugins/dotnet-aspnetcore/skills/minimal-api-file-upload/SKILL.md | `dotnet` (Microsoft) | MIT | adapted | `qrafig-storage` | Useful mechanics; **QRAFIG overrides the shape** — uploads are three calls with capacity reserved first and bytes going straight to the bucket, never a single API-mediated call |
| Testcontainers for .NET | https://github.com/testcontainers/claude-skills/blob/main/plugins/testcontainers/skills/testcontainers-dotnet/SKILL.md | `testcontainers` org (states it is illustrative) | MIT | reused | `qrafig-testing` | Matches `Testcontainers.PostgreSql` / `Testcontainers.Redis` in `Directory.Packages.props` |
| Supabase Postgres Best Practices | https://github.com/supabase/agent-skills/blob/main/skills/supabase-postgres-best-practices/SKILL.md | `supabase` | MIT | adapted | `qrafig-postgres` | Strong locking, index and query rules; **ignore its RLS sections** — QRAFIG isolates in application code through `OrganizationContext`, not with row-level security |
| PostgreSQL Query Plan Analysis | https://github.com/auralshin/coding-skills/blob/main/skills/query-plans/SKILL.md | auralshin | MIT | reused | `qrafig-postgres`, `qrafig-performance` | Focused `EXPLAIN` procedure |
| Keyset Pagination | https://github.com/auralshin/coding-skills/blob/main/skills/keyset-pagination/SKILL.md | auralshin | MIT | reused | `qrafig-postgres` | Matches ADR-0016 cursor pagination |
| Database Queues and Outbox | https://github.com/auralshin/coding-skills/blob/main/skills/database-queues/SKILL.md | auralshin | MIT | adapted | `qrafig-outbox-jobs` | Generic outbox mechanics; **QRAFIG's lease-ownership and no-ordering statements override it** |
| Database Concurrency Audit | https://github.com/Hainrixz/claude-db/blob/main/skills/db-concurrency/SKILL.md | Enrique Rocha | MIT | reused | `qrafig-concurrency` | A checklist-shaped audit that complements QRAFIG's race catalogue |
| Database Multi-Tenancy Isolation Audit | https://github.com/Hainrixz/claude-db/blob/main/skills/db-multitenancy/SKILL.md | Enrique Rocha | MIT | adapted | `qrafig-tenancy` | Good audit questions; **QRAFIG's answer is one application-layer choke point and 404-over-403**, not per-tenant schemas or RLS |
| Database Temporal History Audit | https://github.com/Hainrixz/claude-db/blob/main/skills/db-temporal-history/SKILL.md | Enrique Rocha | MIT | reused | `qrafig-efcore-migrations`, `qrafig-money-finance` | Append-only and history-table review questions |
| Database Types and Precision Audit | https://github.com/Hainrixz/claude-db/blob/main/skills/db-types-precision/SKILL.md | Enrique Rocha | MIT | reused | `qrafig-efcore-migrations` | Money and quantity precision review |
| Distributed Systems Idempotency | https://github.com/triggerdotdev/staff-engineering-skills/blob/main/skills/staff-engineering-skills-idempotency/SKILL.md | triggerdotdev | Apache-2.0 | reused | `qrafig-offline-sync`, `qrafig-outbox-jobs` | Clear treatment of keys, retries and at-least-once |
| Distributed Systems Race Conditions | https://github.com/triggerdotdev/staff-engineering-skills/blob/main/skills/staff-engineering-skills-race-conditions/SKILL.md | triggerdotdev | Apache-2.0 | reused | `qrafig-concurrency` | Complements QRAFIG's catalogue with general race shapes |
| Idempotent Webhook Handler Patterns | https://github.com/hookdeck/webhook-skills/blob/main/skills/webhook-handler-patterns/SKILL.md | hookdeck | MIT | reused | `qrafig-outbox-jobs` | Consumer-side idempotency, which QRAFIG's outbox requires of handlers |
| Auth0 Application Security Review | https://github.com/auth0/agent-skills/blob/main/plugins/auth0/skills/auth0/references/pattern-security/index.md | auth0 | Apache-2.0 | reused | `qrafig-appsec` | Provider-neutral security review questions |
| Auth0 ASP.NET Core API Authorization | https://github.com/auth0/agent-skills/blob/main/plugins/auth0/skills/auth0/references/framework-aspnetcore-api/index.md | auth0 | Apache-2.0 | adapted | `qrafig-authorization` | ASP.NET Core authorization mechanics only; **QRAFIG does not use Auth0** and authorizes by permission code through `OrganizationContext` |
| Next.js (Vercel) | https://github.com/vercel/vercel-plugin/tree/main/skills/nextjs | vercel | see repository | reused | `qrafig-site` | Maintainer-authored Next.js guidance. **Read `node_modules/next/dist/docs/` first** — the installed version is authoritative |
| React Best Practices (Vercel) | https://github.com/vercel/vercel-plugin/tree/main/skills/react-best-practices | vercel | see repository | reused | `qrafig-site` | Maintainer-authored React rules for the interactive components |
| Cloudflare Workers Production Best Practices | https://github.com/cloudflare/skills/blob/main/skills/workers-best-practices/SKILL.md | cloudflare | Apache-2.0 | reused | `qrafig-site` | Only relevant if the site moves to an OpenNext/Workers deployment; today it is a static export on Pages |
| Keyboard Interaction Audit | https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/ | W3C WAI | W3C document licence | reused | `qrafig-site`, `qrafig-desktop-wpf` | Canonical keyboard and focus behaviour; QRAFIG's till must be workable without a mouse |

All of the above were located through, or cross-checked against, the
[`web-skill-atlas`](https://github.com/pneqnp-iswr/web-skill-atlas) dataset (`data/skills.json`),
except `testcontainers/claude-skills`, `wshaddix/dotnet-skills` and `microsoft/win-dev-skills`, which
were found by external search during the gap-driven pass.

---

## 3. Rejected, with reasons

Recording these matters: several are plausible-looking and would actively damage QRAFIG.

| Candidate | Source | Rejected because |
| --- | --- | --- |
| `dotnet-wpf-modern` | https://github.com/wshaddix/dotnet-skills (MIT, Aaron Stannard) | Its central recommendation is **CommunityToolkit.Mvvm source generators**, which QRAFIG deliberately rejects: the view models live in a project with no UI-framework reference, and the MVVM base class is thirty hand-written lines for that reason (ADR-0109). Its baseline is `net8.0-windows`; QRAFIG is `net10.0-windows`. It also covers **none** of QRAFIG's actual WPF defect classes — binding diagnostics, dispatcher affinity, `ObservableCollection` cross-thread, `StaticResource` resolution, `DataTrigger`, virtualization. Kept here as a reference for Host-builder and modern-C# patterns only. |
| `winui-*` (8 skills) and `winui-wpf-migration` | https://github.com/microsoft/win-dev-skills (MIT, Microsoft) | Official and good — and **for WinUI 3 / Windows App SDK**, which QRAFIG evaluated and rejected on deployment and maturity grounds (ADR-0109). `winui-wpf-migration` migrates **away from** WPF. Loading these would push the agent to undo an architectural decision. |
| Syncfusion WPF UI Builder; DevExpress WPF agent skills | vendor repositories | Vendor-control-specific. QRAFIG uses no third-party WPF control library; its design system is its own styles and templates. |
| CRDT / last-write-wins offline sync skills (e.g. SQLite-Sync and similar) | various | **Contradict the architecture.** QRAFIG is server-authoritative with an operation log, four settled outcomes, and reconciliation written *beside* the local record, never over it (ADR-0047, ADR-0118). Automatic merge semantics would destroy the evidence a receipt represents. |
| PostgreSQL row-level-security skills | various | QRAFIG isolates tenants at one application-layer choke point (ADR-0021). Introducing RLS would create a second, divergent isolation mechanism. |
| Prisma / Supabase / PlanetScale / Neon / Timescale product skills | various | Product-specific to stacks QRAFIG does not use. Only the provider-neutral PostgreSQL content in the Supabase skill is referenced, and only as *adapted*. |
| Generic "clean code", "write better code", "senior engineer" prompt bundles | various | No procedure, no verification, no repository grounding. They fail the test in §34 of this system's brief: they can be replaced by the sentence "be careful". |
| Oracle-to-PostgreSQL migration skill family | `github/awesome-copilot` | High quality, and about a migration QRAFIG is not doing. |

---

## 4. What the atlas gave, and where it ran out

`web-skill-atlas` (819 skills, 674 verified) covers the **site** half of QRAFIG well — Next.js, React,
Tailwind, Cloudflare, accessibility, SEO, performance — and gives solid provider-neutral database,
concurrency, security and observability material.

Measured against QRAFIG's task families it is thin exactly where QRAFIG is unusual:

| Family | Atlas entries matching |
| --- | --- |
| Next.js / React / Tailwind / Cloudflare | ~180 |
| Security | ~87 |
| Testing | ~76 |
| PostgreSQL | ~58 |
| Concurrency / idempotency / outbox | ~47 |
| .NET / C# / ASP.NET / EF Core | ~20 |
| SQLite | ~12 |
| POS / retail | ~6 |
| **WPF / XAML / Windows desktop** | **0** |
| **Offline-first / local-first sync** | **0** |

That is not a defect in the atlas — it is a *Web* Skill Atlas, and it says so. It is the reason the
WPF, offline-POS and desktop skills here are original rather than reused. The atlas's own
`docs/gaps.md` independently names SQLite WAL operations, optimistic concurrency tokens, deadlock
diagnosis, transactional outbox and cursor pagination as open gaps, which matches this finding.
