# Web Skill Atlas

**The open-source atlas of AI skills, agent workflows, coding prompts, and reusable instructions for building modern web apps.**

![Skills](https://img.shields.io/badge/skills-253-181717?style=flat-square) ![Verified](https://img.shields.io/badge/verified-149-181717?style=flat-square) ![Categories](https://img.shields.io/badge/categories-24-181717?style=flat-square) ![License](https://img.shields.io/badge/license-MIT-181717?style=flat-square)

253 indexed skills across 24 populated categories and 143 subcategories, traced to 181 upstream sources. The dataset is built for humans browsing GitHub and for agents consuming structured metadata.

Use the atlas to find focused guidance for UI quality, React and Next.js performance, accessibility, testing, security, APIs, databases, SEO, deployment, debugging, and the rest of the web-development lifecycle.

> If the atlas saves you time, star the repository and contribute the skill you expected to find but did not.

## Start here

- Browse the [category index](#categories).
- Use [`data/skills.json`](data/skills.json) as the canonical machine-readable dataset.
- Use [`data/index.min.json`](data/index.min.json) for a compact index.
- Read the [methodology](docs/methodology.md) before relying on status or quality scores.
- For agent consumption, see [`AGENTS.md`](AGENTS.md) and [`llms.txt`](llms.txt).

## A few examples

| Skill | Category | What it covers | Score |
|---|---|---|---:|
| [Anthropic Frontend Design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) | Design | Create distinctive, production-grade frontend interfaces while avoiding generic generated aesthetics. | 91 |
| [Advanced Event Handler Refs](https://github.com/vercel/vercel-plugin/blob/main/skills/react-best-practices/rules/advanced-event-handler-refs.md) | Performance | Apply the Vercel React performance rule for event handler refs. | 88 |
| [Anthropic Webapp Testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Testing | Test local web applications with browser automation and inspect UI behavior. | 88 |
| [Auth](https://github.com/vercel/vercel-plugin/tree/main/skills/auth) | Security | Implement authentication patterns in Vercel applications. | 85 |
| [Supabase Postgres Best Practices](https://github.com/supabase/agent-skills/tree/main/skills/supabase-postgres-best-practices) | Databases | Apply Supabase PostgreSQL guidance for query performance, indexing, RLS, schema design, and locking. | 91 |
| [Keyboard Interaction Audit](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) | Accessibility | Audit interactive controls and composite widgets for keyboard access and predictable focus behavior. | 82 |
| [Access Protected Vercel Deployment](https://github.com/vercel/vercel-plugin/tree/main/skills/access-protected-vercel-deployment) | Deployment | Work with access-protected Vercel deployments. | 85 |
| [Next.js Metadata](https://github.com/vercel/vercel-plugin/blob/main/skills/nextjs/references/metadata.md) | SEO | Apply the Next.js reference guidance for metadata. | 84 |

## Categories

| Category | Skills | Category | Skills |
|---|---:|---|---:|
| [Performance](categories/performance.md) | 75 | [Frontend](categories/frontend.md) | 35 |
| [Design](categories/design.md) | 22 | [Security](categories/security.md) | 20 |
| [Testing](categories/testing.md) | 17 | [Architecture](categories/architecture.md) | 8 |
| [Databases](categories/databases.md) | 8 | [Product](categories/product.md) | 8 |
| [Components](categories/components.md) | 7 | [Backend](categories/backend.md) | 6 |
| [AI Web Development](categories/ai-web-development.md) | 5 | [Deployment](categories/deployment.md) | 5 |
| [Interaction](categories/interaction.md) | 5 | [SEO](categories/seo.md) | 5 |
| [APIs](categories/apis.md) | 4 | [Accessibility](categories/accessibility.md) | 4 |
| [Content](categories/content.md) | 4 | [Debugging](categories/debugging.md) | 3 |
| [DevOps](categories/devops.md) | 3 | [Analytics](categories/analytics.md) | 2 |
| [Code Quality](categories/code-quality.md) | 2 | [Internationalization](categories/internationalization.md) | 2 |
| [PWA](categories/pwa.md) | 2 | [Git / GitHub](categories/git-github.md) | 1 |

Unfilled taxonomy slots are tracked deliberately rather than hidden: `E-commerce`. See [`docs/gaps.md`](docs/gaps.md).

## What counts as a skill

A skill is a reusable instruction set, rule, workflow, or agent procedure aimed at a concrete development task. A framework or library is not counted simply because it exists.

Examples that belong here:

- diagnosing hydration mismatches;
- auditing keyboard navigation;
- reducing unnecessary React re-renders;
- reviewing a PostgreSQL schema;
- generating Playwright smoke tests;
- checking CSP, CORS, cookies, or exposed secrets;
- improving visual hierarchy or responsive layout;
- reviewing metadata, structured data, sitemap, and robots rules.

Granular upstream rule files are indexed separately only when the upstream project publishes them as independently addressable guidance. Collections are not exploded into fake entries just to increase the count.

## Verification

| Status | Meaning |
|---|---|
| `verified` | The original source or official documentation was inspected directly. |
| `partially-verified` | A credible discovery source points to the upstream, but deeper provenance or license review is still pending. |
| `experimental` | Useful candidate kept visible while evidence or maturity is still limited. |
| `deprecated` / `unavailable` / `duplicate` / `archived` | Retained for provenance but excluded from normal browsing. |

`derived-workflow` is a type, not a claim of upstream publication. Derived workflows are built from official documentation and are labeled explicitly.

## Query the dataset

The canonical file is plain JSON, so the atlas can be used without a custom CLI.

```bash
# Security skills scoring 80 or higher
jq '.[] | select(.category == "Security" and .quality_score >= 80)' data/skills.json

# Every Next.js-tagged skill
jq -r '.[] | select(.tags | index("nextjs")) | [.name, .source_url] | @tsv' data/skills.json
```

Generated indexes are also available by category, tag, and framework in `data/`.

## Repository layout

```text
.
├── data/              # canonical dataset, indexes, sources, rejected entries
├── categories/        # generated category pages
├── docs/              # taxonomy, methodology, scoring, research log, gaps
├── scripts/           # validation, generation, deduplication, link checks
├── .github/           # CI, issue templates, pull-request template
├── AGENTS.md
├── llms.txt
├── CONTRIBUTING.md
└── README.md
```

## Data files

- [`data/skills.json`](data/skills.json) — canonical dataset.
- [`data/skills.yaml`](data/skills.yaml) — generated YAML 1.2-compatible mirror.
- [`data/sources.json`](data/sources.json) — upstream source registry.
- [`data/collections.json`](data/collections.json) — registries and collections used for discovery.
- [`data/rejected.json`](data/rejected.json) — rejected and duplicate candidates with reasons.
- [`data/stats.json`](data/stats.json) — generated counts.
- [`data/index.min.json`](data/index.min.json) — compact machine-readable index.

## Quality scoring

Quality scores are not star counts and are not a popularity contest. They measure practical usefulness, specificity, reproducibility, source quality, maintenance, uniqueness, and documentation. A score in the 70s is good; 90+ is intentionally rare.

See [`docs/quality-scoring.md`](docs/quality-scoring.md) for the formula and [`docs/methodology.md`](docs/methodology.md) for inclusion, deduplication, provenance, and verification rules.

## Contributing

Pull requests are welcome for:

- new skills or upstream sources;
- broken or redirected links;
- duplicate reports;
- category and tag corrections;
- license or provenance fixes;
- new taxonomy proposals;
- better descriptions or metadata.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a PR. CI validates required fields, slugs, categories, generated artifacts, and duplicate candidates.

## Research coverage

The project uses broad search, registries, curated collections, upstream repositories, official documentation, and public developer-community references for discovery. It does **not** claim to have exhaustively crawled GitHub, TikTok, Instagram, YouTube, or the entire public web.

Coverage, query families, accepted/rejected candidates, and platform limitations are recorded in [`docs/research-log.md`](docs/research-log.md). Missing areas are tracked in [`docs/gaps.md`](docs/gaps.md).

Last dataset refresh: **2026-08-27**.

## License

Repository code and original metadata are licensed under MIT. Third-party skills remain under their upstream licenses. The atlas primarily indexes metadata and links and does not grant new rights to third-party content. See [`NOTICE`](NOTICE).
