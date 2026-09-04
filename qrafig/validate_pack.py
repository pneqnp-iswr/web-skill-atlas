#!/usr/bin/env python3
"""Validate the QRAFIG skill pack.

    python3 qrafig/validate_pack.py [/path/to/qrafig-checkout]

Checks frontmatter, naming, cross-references, internal links, staleness, and —
when a QRAFIG checkout is given — that every repository path a skill tells the
agent to read actually exists.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent
SKILLS_DIR = PACK / ".claude" / "skills"
REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None

NOT_SKILLS = {"qrafig-original"}
errors: list[str] = []
warnings: list[str] = []

skills = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
names = {p.name for p in skills}

REQUIRED_SECTIONS = ("## Do not",)
RECOMMENDED_SECTIONS = ("## Read first", "## Verification", "## Related skills")
# The router decides what to read and which gates apply; the verification skill *is* the gate
# matrix. Requiring those sections of them would be a tautology.
SECTION_EXEMPT = {
    "qrafig-router": {"## Verification"},
    "qrafig-verification": {"## Verification"},
}

# Volatile facts that must be read from the ledger, never frozen into a skill.
STALE = [
    (re.compile(r"\b2\s?[01]\d\d\b(?=[^%]{0,30}(test|passing))", re.I), "a frozen test count"),
    (re.compile(r"\bschema (?:version )?1[0-9]\b", re.I), "a frozen local schema version"),
    (re.compile(r"\b3[0-9] (?:PostgreSQL )?migrations\b", re.I), "a frozen migration count"),
    (re.compile(r"\b8[0-9][0-9] skills\b"), "a frozen atlas skill count"),
]

for path in skills:
    skill_md = path / "SKILL.md"
    rel = skill_md.relative_to(PACK)
    if not skill_md.is_file():
        errors.append(f"{path.name}: no SKILL.md")
        continue

    text = skill_md.read_text(encoding="utf-8")

    # ---- frontmatter -------------------------------------------------------
    if not text.startswith("---\n"):
        errors.append(f"{rel}: frontmatter must start on the file's first line")
        continue
    end = text.find("\n---\n", 4)
    if end == -1:
        errors.append(f"{rel}: unterminated frontmatter")
        continue
    front, body = text[4:end], text[end + 5 :]

    fields: dict[str, str] = {}
    key = None
    for line in front.splitlines():
        match = re.match(r"^([a-z][\w-]*):\s*(.*)$", line)
        if match:
            key = match.group(1)
            fields[key] = match.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fields[key] += " " + line.strip()

    if fields.get("name") != path.name:
        errors.append(f"{rel}: frontmatter name {fields.get('name')!r} != directory {path.name!r}")
    if not fields.get("description"):
        errors.append(f"{rel}: description is required")
    listing = len(fields.get("description", "")) + len(fields.get("when_to_use", ""))
    if listing > 1536:
        errors.append(f"{rel}: description + when_to_use is {listing} chars, over the 1536 cap")
    elif listing > 1400:
        warnings.append(f"{rel}: description + when_to_use is {listing} chars, close to the cap")

    unknown = set(fields) - {
        "name", "description", "when_to_use", "argument-hint", "arguments",
        "disable-model-invocation", "user-invocable", "allowed-tools", "disallowed-tools",
        "model", "effort", "context", "agent", "background", "hooks", "paths", "shell",
        "metadata", "license", "compatibility",
    }
    if unknown:
        errors.append(f"{rel}: unknown frontmatter field(s) {sorted(unknown)}")

    # ---- body --------------------------------------------------------------
    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"{rel}: missing required section {section!r}")
    for section in RECOMMENDED_SECTIONS:
        if section in SECTION_EXEMPT.get(path.name, set()):
            continue
        if section not in body:
            warnings.append(f"{rel}: no {section!r} section")

    # ---- cross-references --------------------------------------------------
    for referenced in set(re.findall(r"`(qrafig-[a-z-]+)`", body)) - NOT_SKILLS:
        if referenced not in names:
            errors.append(f"{rel}: references unknown skill `{referenced}`")

    # ---- staleness ---------------------------------------------------------
    for pattern, what in STALE:
        for hit in pattern.findall(body):
            warnings.append(f"{rel}: possibly {what} — {hit!r}; read it from the ledger instead")

    # ---- repository paths --------------------------------------------------
    if REPO:
        for candidate in set(re.findall(r"`((?:backend|desktop|apps|docs)/[\w./-]+)`", body)):
            probe = candidate.rstrip("/")
            if probe.endswith("*") or "…" in probe:
                continue
            if not (REPO / probe).exists() and not (PACK / probe).exists():
                errors.append(f"{rel}: repository path does not exist: {probe}")

# ---- CLAUDE.md ------------------------------------------------------------
claude = (PACK / "CLAUDE.md").read_text(encoding="utf-8")
for referenced in set(re.findall(r"`(qrafig-[a-z-]+)`", claude)) - NOT_SKILLS:
    if referenced not in names:
        errors.append(f"CLAUDE.md: references unknown skill `{referenced}`")
listed = set(re.findall(r"^\| `(qrafig-[a-z-]+)` \|", claude, re.M))
if listed != names:
    if names - listed:
        errors.append(f"CLAUDE.md: skill index is missing {sorted(names - listed)}")
    if listed - names:
        errors.append(f"CLAUDE.md: skill index names non-existent {sorted(listed - names)}")
if len(claude.splitlines()) > 200:
    warnings.append(f"CLAUDE.md is {len(claude.splitlines())} lines — it loads on every task, keep it lean")

# ---- registry and manifest -------------------------------------------------
for doc in ("docs/ai/skills.md", "docs/ai/sources.md", "docs/ai/routing-eval.md"):
    path = PACK / doc
    if not path.is_file():
        errors.append(f"missing {doc}")
        continue
    content = path.read_text(encoding="utf-8")
    for referenced in set(re.findall(r"`(qrafig-[a-z-]+)`", content)) - NOT_SKILLS:
        if referenced not in names:
            errors.append(f"{doc}: references unknown skill `{referenced}`")
    for target in re.findall(r"\]\(([^)#][^)]*)\)", content):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (path.parent / target).exists():
            errors.append(f"{doc}: broken relative link -> {target}")

registry = (PACK / "docs/ai/skills.md").read_text(encoding="utf-8")
in_registry = set(re.findall(r"`(qrafig-[a-z-]+)`", registry))
if names - in_registry:
    errors.append(f"docs/ai/skills.md: not registered: {sorted(names - in_registry)}")
manifest = (PACK / "docs/ai/sources.md").read_text(encoding="utf-8")
if names - set(re.findall(r"`(qrafig-[a-z-]+)`", manifest)):
    errors.append(f"docs/ai/sources.md: not in the manifest: {sorted(names - set(re.findall(r'`(qrafig-[a-z-]+)`', manifest)))}")

# ---- ADR references resolve ------------------------------------------------
if REPO:
    adr_file = REPO / "docs" / "architecture-decisions.md"
    if adr_file.is_file():
        existing_adrs = set(re.findall(r"^## (ADR-\d{4}) ", adr_file.read_text(encoding="utf-8"), re.M))
        cited: set[str] = set()
        for md in sorted(PACK.rglob("*.md")):
            for ref in re.findall(r"ADR-\d{4}", md.read_text(encoding="utf-8")):
                cited.add(ref)
                if ref not in existing_adrs:
                    errors.append(f"{md.relative_to(PACK)}: cites {ref}, which is not in the ADR record")
        print(f"ADR references: {len(cited)} distinct, out of {len(existing_adrs)} recorded")
    else:
        warnings.append("no docs/architecture-decisions.md in the given checkout; ADR references unchecked")
else:
    warnings.append("no QRAFIG checkout given; repository paths and ADR references unchecked")

# ---- report ----------------------------------------------------------------
print(f"skills: {len(skills)}")
for warning in warnings:
    print(f"WARN  {warning}")
for error in errors:
    print(f"ERROR {error}")
print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
