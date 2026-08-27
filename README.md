# Web Skill Atlas

**Source-backed, reusable AI skills for designing, building, testing, debugging, and shipping modern web applications.**

<!-- GENERATED:BADGES:START -->
[![Skills](https://img.shields.io/badge/skills-363-181717?style=flat-square)](data/skills.json) [![Verified](https://img.shields.io/badge/verified-195-181717?style=flat-square)](docs/methodology.md) [![Categories](https://img.shields.io/badge/categories-24-181717?style=flat-square)](#browse) [![Validation](https://github.com/pneqnp-iswr/web-skill-atlas/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/pneqnp-iswr/web-skill-atlas/actions/workflows/validate.yml) [![License](https://img.shields.io/badge/license-MIT-181717?style=flat-square)](LICENSE)
<!-- GENERATED:BADGES:END -->

<!-- GENERATED:STATS:START -->
**363** skills · **195** verified · **24/25** categories populated · **174** subcategories · **202** sources · updated **2026-08-27**
<!-- GENERATED:STATS:END -->

Web Skill Atlas indexes reusable AI skills and agent workflows across public repositories, registries, tool ecosystems, and official documentation, then normalizes them around canonical sources.

This is not a generated prompt dump. Entries are sourced, classified, deduplicated, and linked to their public origin. The catalog is tool-independent and available as machine-readable data.

[Browse](#browse) · [Example skills](#example-skills) · [Dataset](#dataset) · [Verification](#verification) · [Contributing](#contributing)

If the atlas saves you time, consider starring the repository.

<a id="categories"></a>

## Browse

Browse the generated category pages or search the full dataset directly.

<!-- GENERATED:BROWSE:START -->
| Category | Skills | Category | Skills |
|---|---:|---|---:|
| [Design](categories/design.md) | 132 | [Performance](categories/performance.md) | 75 |
| [Frontend](categories/frontend.md) | 35 | [Security](categories/security.md) | 20 |
| [Testing](categories/testing.md) | 17 | [Architecture](categories/architecture.md) | 8 |
| [Databases](categories/databases.md) | 8 | [Product](categories/product.md) | 8 |
| [Components](categories/components.md) | 7 | [Backend](categories/backend.md) | 6 |
| [AI Web Development](categories/ai-web-development.md) | 5 | [Deployment](categories/deployment.md) | 5 |
| [Interaction](categories/interaction.md) | 5 | [SEO](categories/seo.md) | 5 |
| [Accessibility](categories/accessibility.md) | 4 | [APIs](categories/apis.md) | 4 |
| [Content](categories/content.md) | 4 | [Debugging](categories/debugging.md) | 3 |
| [DevOps](categories/devops.md) | 3 | [Analytics](categories/analytics.md) | 2 |
| [Code Quality](categories/code-quality.md) | 2 | [Internationalization](categories/internationalization.md) | 2 |
| [PWA](categories/pwa.md) | 2 | [Git / GitHub](categories/git-github.md) | 1 |
<!-- GENERATED:BROWSE:END -->

## Example skills

A small cross-section of high-quality entries already in the dataset:

<!-- GENERATED:EXAMPLES:START -->
| Skill | Area | What it does |
|---|---|---|
| [UI Design](https://github.com/mblode/agent-skills/blob/main/skills/ui-design/SKILL.md) | Design | Design, build, and audit web UI through explicit direction, build, audit, options, scaffold, and retrofit modes. |
| [Nextjs](https://github.com/vercel/vercel-plugin/tree/main/skills/nextjs) | Frontend | Apply current Next.js implementation guidance. |
| [Advanced Event Handler Refs](https://github.com/vercel/vercel-plugin/blob/main/skills/react-best-practices/rules/advanced-event-handler-refs.md) | Performance | Apply the Vercel React performance rule for event handler refs. |
| [Keyboard Interaction Audit](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) | Accessibility | Audit interactive controls and composite widgets for keyboard access and predictable focus behavior. |
| [Anthropic Webapp Testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Testing | Test local web applications with browser automation and inspect UI behavior. |
| [Auth](https://github.com/vercel/vercel-plugin/tree/main/skills/auth) | Security | Implement authentication patterns in Vercel applications. |
| [REST API Design Review](https://www.rfc-editor.org/rfc/rfc9110) | APIs | Review resource modeling, HTTP semantics, errors, idempotency, pagination, and versioning. |
| [Supabase Postgres Best Practices](https://github.com/supabase/agent-skills/tree/main/skills/supabase-postgres-best-practices) | Databases | Apply Supabase PostgreSQL guidance for query performance, indexing, RLS, schema design, and locking. |
| [Access Protected Vercel Deployment](https://github.com/vercel/vercel-plugin/tree/main/skills/access-protected-vercel-deployment) | Deployment | Work with access-protected Vercel deployments. |
<!-- GENERATED:EXAMPLES:END -->

## What counts as a skill?

A skill is a reusable instruction set, rule, workflow, or agent procedure for a concrete development task.

React is not a skill; a repeatable React performance procedure can be. Figma is not a skill; a reusable design-system audit can be. Collections are not split into invented variants just to increase the count.

## Dataset

[`data/skills.json`](data/skills.json) is the canonical dataset. [`data/index.min.json`](data/index.min.json) is the compact index. Generated indexes by category, tag, and framework are also available in [`data/`](data/).

```bash
curl -fsSL https://raw.githubusercontent.com/pneqnp-iswr/web-skill-atlas/main/data/skills.json \
  | jq '.[] | select(.tags | index("nextjs")) | {name, source_url}'
```

For coding agents, [`AGENTS.md`](AGENTS.md) and [`llms.txt`](llms.txt) point to the canonical files and repository conventions.

## Verification

| Status | Meaning |
|---|---|
| `verified` | The original source or official documentation was inspected directly. |
| `partially-verified` | A credible source is known, but deeper provenance or license review is still pending. |
| `experimental` | A useful candidate remains visible while evidence or maturity is limited. |
| `deprecated` / `unavailable` / `duplicate` / `archived` | Retained for provenance and excluded from normal browsing. |

Canonical sources are preferred over registry mirrors, curated-list copies, and social posts. Forks and mirrors are not counted as separate skills by default. `derived-workflow` is a type, not a claim that an upstream project published that exact skill.

Quality scores measure practical usefulness, specificity, reproducibility, source quality, maintenance, uniqueness, and documentation. See [`docs/quality-scoring.md`](docs/quality-scoring.md) and [`docs/methodology.md`](docs/methodology.md).

## Contributing

Found a missing skill or a bad entry? Use the [issue forms](https://github.com/pneqnp-iswr/web-skill-atlas/issues/new/choose) or open a pull request.

For a new entry, provide at least:

- name and concise purpose;
- canonical source URL;
- suggested category;
- enough source detail to distinguish it from mirrors or nearby skills.

Before opening a PR:

```bash
python scripts/validate.py
python scripts/deduplicate.py
python scripts/generate.py
python scripts/validate_issue_forms.py
python scripts/scan_secrets.py
git diff --exit-code
```

The full contribution rules are in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Methodology

Discovery leads come from repositories, registries, official documentation, curated collections, and publicly indexed developer-community sources. Discovery is not verification: the atlas prefers the original source and records incomplete provenance explicitly.

Coverage is broad, not exhaustive. Search engines, GitHub indexing, social platforms, deleted repositories, and private or non-indexed sources all impose limits, and verification can lag behind upstream changes. See [`docs/research-log.md`](docs/research-log.md) and [`docs/gaps.md`](docs/gaps.md).

<!-- GENERATED:UPDATED:START -->
Last dataset refresh: **2026-08-27**.
<!-- GENERATED:UPDATED:END -->

## Repository layout

```text
.
├── data/          canonical dataset, source registry, generated indexes
├── categories/    generated category pages
├── docs/          methodology, taxonomy, scoring, research notes
├── scripts/       validation, generation, deduplication, link checks
├── assets/        repository presentation assets
└── .github/       CI, issue forms, pull-request template
```

See [`CHANGELOG.md`](CHANGELOG.md) for dataset and repository changes.

## License

Web Skill Atlas code and original repository metadata are licensed under MIT where applicable. Third-party skills remain subject to their original licenses; indexing a source does not grant additional rights to its content. See [`NOTICE`](NOTICE).
