#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISSUE_FORMS = ROOT / ".github" / "ISSUE_TEMPLATE"

errors = []
forms = sorted(ISSUE_FORMS.glob("*.yml")) + sorted(ISSUE_FORMS.glob("*.yaml"))
checked = 0

for path in forms:
    if path.name == "config.yml":
        continue
    checked += 1
    text = path.read_text(encoding="utf-8")
    top_level = {}

    for line in text.splitlines():
        if not line or line[0].isspace() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        top_level[key.strip()] = value.strip()

    for required in ("name", "description", "body"):
        if required not in top_level:
            errors.append(f"{path.relative_to(ROOT)}: missing top-level '{required}'")

    if "about" in top_level:
        errors.append(
            f"{path.relative_to(ROOT)}: top-level 'about' is for Markdown templates; "
            "use 'description' for YAML issue forms"
        )

    if top_level.get("body") not in ("", None):
        errors.append(f"{path.relative_to(ROOT)}: 'body' must be a YAML sequence")

if errors:
    for error in errors:
        print(f"ERROR {error}")
    raise SystemExit(1)

print(f"validated_issue_forms={checked}")
