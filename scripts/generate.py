#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
from datetime import date
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

skills = json.loads((DATA / "skills.json").read_text(encoding="utf-8"))
cats = json.loads((DATA / "categories.json").read_text(encoding="utf-8"))
sources = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
rejected = json.loads((DATA / "rejected.json").read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    value = value.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def esc(text: str) -> str:
    return str(text).replace("|", "\\|")


visible = [s for s in skills if s["status"] in {"verified", "partially-verified", "experimental"}]
category_counts = Counter(s["category"] for s in visible)
subcategories = {(s["category"], s["subcategory"]) for s in visible}

stats = {
    "total_skills": len(skills),
    "visible_skills": len(visible),
    "verified": sum(s["status"] == "verified" for s in skills),
    "partially_verified": sum(s["status"] == "partially-verified" for s in skills),
    "experimental": sum(s["status"] == "experimental" for s in skills),
    "categories_total": len(cats),
    "categories_populated": sum(category_counts[c["name"]] > 0 for c in cats),
    "subcategories_populated": len(subcategories),
    "unique_sources": len(sources),
    "rejected": len(rejected),
    "last_updated": date.today().isoformat(),
    "category_counts": dict(sorted(category_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
}

(DATA / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(DATA / "index.min.json").write_text(
    json.dumps(
        [
            {
                "n": s["name"],
                "s": s["slug"],
                "c": s["category"],
                "u": s["source_url"],
                "q": s["quality_score"],
                "v": s["status"],
            }
            for s in visible
        ],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)

# JSON is valid YAML 1.2. Keeping this mirror dependency-free prevents PyYAML
# from becoming a requirement for contributors and CI.
(DATA / "skills.yaml").write_text(
    "# Generated mirror of data/skills.json. JSON is valid YAML 1.2.\n"
    + json.dumps(skills, indent=2, ensure_ascii=False)
    + "\n",
    encoding="utf-8",
)

for output_name, field in [
    ("categories-index", "category"),
    ("tags-index", "tags"),
    ("frameworks-index", "frameworks"),
]:
    index = defaultdict(list)
    for skill in visible:
        values = skill[field] if isinstance(skill[field], list) else [skill[field]]
        for value in values:
            index[value].append(skill["slug"])
    (DATA / f"{output_name}.json").write_text(
        json.dumps(dict(sorted(index.items())), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

# Category pages
category_dir = ROOT / "categories"
category_dir.mkdir(exist_ok=True)
for old in category_dir.glob("*.md"):
    old.unlink()

for category in cats:
    items = [s for s in visible if s["category"] == category["name"]]

    lines = [
        f"# {category['name']}",
        "",
        f"{len(items)} indexed skills. [Back to the atlas](../README.md#categories).",
        "",
        "| Skill | Subcategory | Status | Score | Source |",
        "|---|---|---|---:|---|",
    ]
    for skill in sorted(items, key=lambda x: (x["subcategory"].lower(), x["name"].lower())):
        lines.append(
            f"| [{esc(skill['name'])}]({skill['source_url']}) | {esc(skill['subcategory'])} | "
            f"{skill['status']} | {skill['quality_score']} | {esc(skill['source_platform'])} |"
        )
    if not items:
        lines += ["", "No indexed skills yet. This taxonomy slot is intentionally kept visible until a qualifying source is added."]
    lines += ["", "Generated from `data/skills.json`. Do not edit counts manually.", ""]
    (category_dir / f"{slugify(category['name'])}.md").write_text("\n".join(lines), encoding="utf-8")

# Pick representative high-quality skills from distinct areas for the front page.
featured_categories = [
    "Design",
    "Performance",
    "Testing",
    "Security",
    "Databases",
    "Accessibility",
    "Deployment",
    "SEO",
]
featured = []
for category in featured_categories:
    candidates = [s for s in visible if s["category"] == category]
    if candidates:
        featured.append(max(candidates, key=lambda s: (s["quality_score"], s["status"] == "verified")))

# Compact category table: two categories per row.
category_pairs = list(stats["category_counts"].items())
category_rows = []
for i in range(0, len(category_pairs), 2):
    left_name, left_count = category_pairs[i]
    if i + 1 < len(category_pairs):
        right_name, right_count = category_pairs[i + 1]
        right_cell = f"[{right_name}](categories/{slugify(right_name)}.md)"
        right_count_cell = str(right_count)
    else:
        right_cell = ""
        right_count_cell = ""
    category_rows.append(
        f"| [{left_name}](categories/{slugify(left_name)}.md) | {left_count} | {right_cell} | {right_count_cell} |"
    )

empty_categories = [c["name"] for c in cats if category_counts[c["name"]] == 0]

readme = [
    "# Web Skill Atlas",
    "",
    "**The open-source atlas of AI skills, agent workflows, coding prompts, and reusable instructions for building modern web apps.**",
    "",
    f"![Skills](https://img.shields.io/badge/skills-{stats['total_skills']}-181717?style=flat-square) "
    f"![Verified](https://img.shields.io/badge/verified-{stats['verified']}-181717?style=flat-square) "
    f"![Categories](https://img.shields.io/badge/categories-{stats['categories_populated']}-181717?style=flat-square) "
    "![License](https://img.shields.io/badge/license-MIT-181717?style=flat-square)",
    "",
    f"{stats['total_skills']} indexed skills across {stats['categories_populated']} populated categories and "
    f"{stats['subcategories_populated']} subcategories, traced to {stats['unique_sources']} upstream sources. "
    "The dataset is built for humans browsing GitHub and for agents consuming structured metadata.",
    "",
    "Use the atlas to find focused guidance for UI quality, React and Next.js performance, accessibility, testing, security, APIs, databases, SEO, deployment, debugging, and the rest of the web-development lifecycle.",
    "",
    "> If the atlas saves you time, star the repository and contribute the skill you expected to find but did not.",
    "",
    "## Start here",
    "",
    "- Browse the [category index](#categories).",
    "- Use [`data/skills.json`](data/skills.json) as the canonical machine-readable dataset.",
    "- Use [`data/index.min.json`](data/index.min.json) for a compact index.",
    "- Read the [methodology](docs/methodology.md) before relying on status or quality scores.",
    "- For agent consumption, see [`AGENTS.md`](AGENTS.md) and [`llms.txt`](llms.txt).",
    "",
    "## A few examples",
    "",
    "| Skill | Category | What it covers | Score |",
    "|---|---|---|---:|",
]

for skill in featured:
    readme.append(
        f"| [{esc(skill['name'])}]({skill['source_url']}) | {esc(skill['category'])} | "
        f"{esc(skill['description'])} | {skill['quality_score']} |"
    )

readme += [
    "",
    "## Categories",
    "",
    "| Category | Skills | Category | Skills |",
    "|---|---:|---|---:|",
    *category_rows,
]

if empty_categories:
    readme += [
        "",
        "Unfilled taxonomy slots are tracked deliberately rather than hidden: "
        + ", ".join(f"`{name}`" for name in empty_categories)
        + ". See [`docs/gaps.md`](docs/gaps.md).",
    ]

readme += [
    "",
    "## What counts as a skill",
    "",
    "A skill is a reusable instruction set, rule, workflow, or agent procedure aimed at a concrete development task. A framework or library is not counted simply because it exists.",
    "",
    "Examples that belong here:",
    "",
    "- diagnosing hydration mismatches;",
    "- auditing keyboard navigation;",
    "- reducing unnecessary React re-renders;",
    "- reviewing a PostgreSQL schema;",
    "- generating Playwright smoke tests;",
    "- checking CSP, CORS, cookies, or exposed secrets;",
    "- improving visual hierarchy or responsive layout;",
    "- reviewing metadata, structured data, sitemap, and robots rules.",
    "",
    "Granular upstream rule files are indexed separately only when the upstream project publishes them as independently addressable guidance. Collections are not exploded into fake entries just to increase the count.",
    "",
    "## Verification",
    "",
    "| Status | Meaning |",
    "|---|---|",
    "| `verified` | The original source or official documentation was inspected directly. |",
    "| `partially-verified` | A credible discovery source points to the upstream, but deeper provenance or license review is still pending. |",
    "| `experimental` | Useful candidate kept visible while evidence or maturity is still limited. |",
    "| `deprecated` / `unavailable` / `duplicate` / `archived` | Retained for provenance but excluded from normal browsing. |",
    "",
    "`derived-workflow` is a type, not a claim of upstream publication. Derived workflows are built from official documentation and are labeled explicitly.",
    "",
    "## Query the dataset",
    "",
    "The canonical file is plain JSON, so the atlas can be used without a custom CLI.",
    "",
    "```bash",
    "# Security skills scoring 80 or higher",
    "jq '.[] | select(.category == \"Security\" and .quality_score >= 80)' data/skills.json",
    "",
    "# Every Next.js-tagged skill",
    "jq -r '.[] | select(.tags | index(\"nextjs\")) | [.name, .source_url] | @tsv' data/skills.json",
    "```",
    "",
    "Generated indexes are also available by category, tag, and framework in `data/`.",
    "",
    "## Repository layout",
    "",
    "```text",
    ".",
    "├── data/              # canonical dataset, indexes, sources, rejected entries",
    "├── categories/        # generated category pages",
    "├── docs/              # taxonomy, methodology, scoring, research log, gaps",
    "├── scripts/           # validation, generation, deduplication, link checks",
    "├── .github/           # CI, issue templates, pull-request template",
    "├── AGENTS.md",
    "├── llms.txt",
    "├── CONTRIBUTING.md",
    "└── README.md",
    "```",
    "",
    "## Data files",
    "",
    "- [`data/skills.json`](data/skills.json) — canonical dataset.",
    "- [`data/skills.yaml`](data/skills.yaml) — generated YAML 1.2-compatible mirror.",
    "- [`data/sources.json`](data/sources.json) — upstream source registry.",
    "- [`data/collections.json`](data/collections.json) — registries and collections used for discovery.",
    "- [`data/rejected.json`](data/rejected.json) — rejected and duplicate candidates with reasons.",
    "- [`data/stats.json`](data/stats.json) — generated counts.",
    "- [`data/index.min.json`](data/index.min.json) — compact machine-readable index.",
    "",
    "## Quality scoring",
    "",
    "Quality scores are not star counts and are not a popularity contest. They measure practical usefulness, specificity, reproducibility, source quality, maintenance, uniqueness, and documentation. A score in the 70s is good; 90+ is intentionally rare.",
    "",
    "See [`docs/quality-scoring.md`](docs/quality-scoring.md) for the formula and [`docs/methodology.md`](docs/methodology.md) for inclusion, deduplication, provenance, and verification rules.",
    "",
    "## Contributing",
    "",
    "Pull requests are welcome for:",
    "",
    "- new skills or upstream sources;",
    "- broken or redirected links;",
    "- duplicate reports;",
    "- category and tag corrections;",
    "- license or provenance fixes;",
    "- new taxonomy proposals;",
    "- better descriptions or metadata.",
    "",
    "Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a PR. CI validates required fields, slugs, categories, generated artifacts, and duplicate candidates.",
    "",
    "## Research coverage",
    "",
    "The project uses broad search, registries, curated collections, upstream repositories, official documentation, and public developer-community references for discovery. It does **not** claim to have exhaustively crawled GitHub, TikTok, Instagram, YouTube, or the entire public web.",
    "",
    "Coverage, query families, accepted/rejected candidates, and platform limitations are recorded in [`docs/research-log.md`](docs/research-log.md). Missing areas are tracked in [`docs/gaps.md`](docs/gaps.md).",
    "",
    f"Last dataset refresh: **{stats['last_updated']}**.",
    "",
    "## License",
    "",
    "Repository code and original metadata are licensed under MIT. Third-party skills remain under their upstream licenses. The atlas primarily indexes metadata and links and does not grant new rights to third-party content. See [`NOTICE`](NOTICE).",
    "",
]

(ROOT / "README.md").write_text("\n".join(readme), encoding="utf-8")
print(json.dumps(stats, indent=2, ensure_ascii=False))
