#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
README = ROOT / "README.md"

skills = json.loads((DATA / "skills.json").read_text(encoding="utf-8"))
cats = json.loads((DATA / "categories.json").read_text(encoding="utf-8"))
sources = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
rejected = json.loads((DATA / "rejected.json").read_text(encoding="utf-8"))

VISIBLE_STATUSES = {"verified", "partially-verified", "experimental"}


def slugify(value: str) -> str:
    value = value.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def esc(text: str) -> str:
    return str(text).replace("|", "\\|")


def replace_generated_block(text: str, name: str, body: list[str]) -> str:
    start = f"<!-- GENERATED:{name}:START -->"
    end = f"<!-- GENERATED:{name}:END -->"
    if start not in text or end not in text:
        raise RuntimeError(f"README is missing generated block markers for {name}")
    replacement = start + "\n" + "\n".join(body).rstrip() + "\n" + end
    pattern = re.escape(start) + r".*?" + re.escape(end)
    return re.sub(pattern, lambda _: replacement, text, flags=re.S)


visible = [s for s in skills if s["status"] in VISIBLE_STATUSES]
category_counts = Counter(s["category"] for s in visible)
subcategories = {(s["category"], s["subcategory"]) for s in visible}
verification_dates = [s.get("last_verified", "") for s in skills] + [s.get("last_checked", "") for s in sources]
last_updated = max((d for d in verification_dates if d), default="unknown")

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
    "last_updated": last_updated,
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

# JSON is valid YAML 1.2. Keeping this mirror dependency-free avoids a runtime dependency.
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

# Generated category pages. Every taxonomy category keeps a stable path, including empty slots.
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

# README generated blocks. Keep the examples stable and deliberately broad.
featured_slugs = [
    "mblode-ui-design",
    "nextjs",
    "advanced-event-handler-refs",
    "keyboard-interaction-audit",
    "anthropic-webapp-testing",
    "vercel-auth",
    "rest-api-design-review",
    "supabase-postgres-best-practices",
    "access-protected-vercel-deployment",
]
by_slug = {s["slug"]: s for s in visible}
missing_featured = [slug for slug in featured_slugs if slug not in by_slug]
if missing_featured:
    raise RuntimeError(f"README featured skills are missing from the dataset: {missing_featured}")
featured = [by_slug[slug] for slug in featured_slugs]

all_category_pairs = sorted(
    ((c["name"], category_counts[c["name"]]) for c in cats),
    key=lambda kv: (-kv[1], kv[0].lower()),
)
category_rows = []
for i in range(0, len(all_category_pairs), 2):
    left_name, left_count = all_category_pairs[i]
    left = f"[{left_name}](categories/{slugify(left_name)}.md)"
    if i + 1 < len(all_category_pairs):
        right_name, right_count = all_category_pairs[i + 1]
        right = f"[{right_name}](categories/{slugify(right_name)}.md)"
        category_rows.append(f"| {left} | {left_count} | {right} | {right_count} |")
    else:
        category_rows.append(f"| {left} | {left_count} |  |  |")

badges = [
    f"[![Skills](https://img.shields.io/badge/skills-{stats['total_skills']}-181717?style=flat-square)](data/skills.json)",
    f"[![Verified](https://img.shields.io/badge/verified-{stats['verified']}-181717?style=flat-square)](docs/methodology.md)",
    f"[![Categories](https://img.shields.io/badge/categories-{stats['categories_populated']}-181717?style=flat-square)](#browse)",
    "[![Validation](https://github.com/pneqnp-iswr/web-skill-atlas/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/pneqnp-iswr/web-skill-atlas/actions/workflows/validate.yml)",
    "[![License](https://img.shields.io/badge/license-MIT-181717?style=flat-square)](LICENSE)",
]

stats_line = (
    f"**{stats['total_skills']}** skills · **{stats['verified']}** verified · "
    f"**{stats['categories_populated']}/{stats['categories_total']}** categories populated · "
    f"**{stats['subcategories_populated']}** subcategories · **{stats['unique_sources']}** sources · "
    f"updated **{stats['last_updated']}**"
)

example_lines = [
    "| Skill | Area | What it does |",
    "|---|---|---|",
]
for skill in featured:
    example_lines.append(
        f"| [{esc(skill['name'])}]({skill['source_url']}) | {esc(skill['category'])} | {esc(skill['description'])} |"
    )

readme = README.read_text(encoding="utf-8")
readme = replace_generated_block(readme, "BADGES", [" ".join(badges)])
readme = replace_generated_block(readme, "STATS", [stats_line])
readme = replace_generated_block(
    readme,
    "BROWSE",
    [
        "| Category | Skills | Category | Skills |",
        "|---|---:|---|---:|",
        *category_rows,
    ],
)
readme = replace_generated_block(readme, "EXAMPLES", example_lines)
readme = replace_generated_block(readme, "UPDATED", [f"Last dataset refresh: **{stats['last_updated']}**."])
README.write_text(readme.rstrip() + "\n", encoding="utf-8")

print(json.dumps(stats, indent=2, ensure_ascii=False))
