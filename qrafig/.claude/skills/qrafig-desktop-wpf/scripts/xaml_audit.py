#!/usr/bin/env python3
"""Static audits for WPF defect classes that compile cleanly and fail at run time.

Run from the QRAFIG repository root:

    python .claude/skills/qrafig-desktop-wpf/scripts/xaml_audit.py

This is a *pre-filter*, not a substitute for the live QRAFIG.exe smoke (ADR-0191).
It finds names and shapes; only a running application proves rendering.
Every finding is a question. Confirm it against the file before changing anything.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
DESKTOP = ROOT / "desktop" / "src" / "Qrafig.Desktop"
if not DESKTOP.is_dir():
    sys.exit(f"not a QRAFIG checkout: {DESKTOP} does not exist")

XAML = sorted(DESKTOP.rglob("*.xaml"))
SOURCE = {path: path.read_text(encoding="utf-8") for path in XAML}
findings: list[tuple[str, str, int, str]] = []


def add(kind: str, path: Path, offset: int, detail: str) -> None:
    line = SOURCE[path].count("\n", 0, offset) + 1
    findings.append((kind, str(path.relative_to(ROOT)), line, detail))


# --------------------------------------------------------------- 1. resource keys
# A StaticResource key that exists nowhere throws inside InitializeComponent(). BAML
# compiles without resolving it, and navigation through a TwoWay binding's source
# setter swallows the exception: the previous workspace simply stays on screen.
defined = {key for text in SOURCE.values() for key in re.findall(r'x:Key="([^"]+)"', text)}
FRAMEWORK = ("{x:", "{DynamicResource", "System", "Sys")

for path, text in SOURCE.items():
    for match in re.finditer(r"\{StaticResource\s+([^}\s]+)\s*\}", text):
        key = match.group(1)
        if key.startswith(FRAMEWORK) or key in defined:
            continue
        add("UNDEFINED-STATICRESOURCE", path, match.start(), key)


# ------------------------------------------------ 2. style applied to a wrong target
# A style whose TargetType is not the element it is applied to throws at XAML load.
# `ElementStyle` and `HeaderStyle` on a DataGrid column target the generated element
# and the column header, so they are excluded deliberately.
keyed_styles: dict[str, str] = {}
implicit_styles: set[str] = set()
for text in SOURCE.values():
    for key, target in re.findall(r'<Style\s+x:Key="([^"]+)"\s+TargetType="([^"]+)"', text):
        keyed_styles[key] = target.split(":")[-1].replace("{x:Type", "").strip("{} ").strip()
    for target in re.findall(r"<Style\s+TargetType=\"([^\"]+)\"", text):
        implicit_styles.add(target.split(":")[-1].replace("{x:Type", "").strip("{} ").strip())

APPLIED = re.compile(r"<([A-Za-z][\w]*)\b[^<>]*?(?<![\w.])Style=\"\{StaticResource\s+([^}\s]+)\s*\}\"", re.S)
for path, text in SOURCE.items():
    for match in APPLIED.finditer(text):
        element, key = match.group(1), match.group(2)
        target = keyed_styles.get(key)
        if target and target != element:
            add("STYLE-TARGETTYPE-MISMATCH", path, match.start(),
                f"<{element}> uses '{key}' whose TargetType is {target}")


# ------------------------------------------------------ 3. Tag compared against a bool
# Tag is typed `object`. A property Trigger with Value="True" compares a boxed bool
# against the *string* "True" and never matches — the tab strip renders with nothing
# selected, in every theme, silently. Use a DataTrigger binding Self.Tag.
# A Tag holding a real string (WindowChrome's native hover states) is fine.
for path, text in SOURCE.items():
    for match in re.finditer(r'<Trigger\s+Property="Tag"\s+Value="(True|False)"', text):
        add("TAG-TRIGGER-NEVER-MATCHES", path, match.start(),
            f'Value="{match.group(1)}" — use <DataTrigger Binding="{{Binding RelativeSource='
            '{RelativeSource Self}, Path=Tag}}">')


# --------------------------------- 4. DataContext override shadowing a sibling binding
# A DataContext set on the same element as another binding re-points that binding at
# the child view model, silently. Five Finance sections rendered permanently visible
# and stacked for exactly this reason. The fix is an explicit source on the sibling —
# RelativeSource AncestorType=UserControl, ElementName, or Source — so those pass.
ELEMENT = re.compile(r"<[A-Za-z][\w:.]*\s[^<>]*?/?>", re.S)
BINDING = re.compile(r'(\w[\w.:]*)="(\{Binding[^"]*)"')
for path, text in SOURCE.items():
    for match in ELEMENT.finditer(text):
        element = match.group(0)
        if "DataContext=" not in element:
            continue
        unrooted = [
            name for name, expr in BINDING.findall(element)
            if name != "DataContext"
            and "RelativeSource" not in expr and "ElementName" not in expr and "Source=" not in expr
        ]
        if unrooted:
            add("DATACONTEXT-SHADOWS-BINDING", path, match.start(),
                "DataContext set beside un-rooted " + ", ".join(sorted(set(unrooted))))


# ------------------------------------------------------------ 5. unstyled list control
# A control with no style renders in WPF's white default inside a dark window.
# Implicit styles live in Theme/Controls.xaml and apply application-wide, so they count.
LIST_CONTROLS = ("ListView", "ListBox", "DataGrid", "TreeView", "ComboBox")
for path, text in SOURCE.items():
    for match in re.finditer(rf"<({'|'.join(LIST_CONTROLS)})\b((?:[^<>])*?)>", text):
        control, attrs = match.group(1), match.group(2)
        if "Style=" in attrs or control in implicit_styles:
            continue
        add("UNSTYLED-CONTROL", path, match.start(), f"<{control}> has neither a Style nor an implicit style")


# --------------------------------------------------------- 6. TwoWay onto a read-only
for path, text in SOURCE.items():
    for match in re.finditer(r"\{Binding[^}]*Mode=TwoWay[^}]*\}", text):
        if "Path=" in match.group(0) or re.match(r"\{Binding\s+[A-Za-z]", match.group(0)):
            continue
        add("TWOWAY-NO-PATH", path, match.start(), "TwoWay binding with no explicit path")


KINDS = [
    "UNDEFINED-STATICRESOURCE",
    "STYLE-TARGETTYPE-MISMATCH",
    "TAG-TRIGGER-NEVER-MATCHES",
    "DATACONTEXT-SHADOWS-BINDING",
    "UNSTYLED-CONTROL",
    "TWOWAY-NO-PATH",
]

for kind in KINDS:
    hits = [f for f in findings if f[0] == kind]
    print(f"\n== {kind}: {len(hits)}")
    for _, path, line, detail in hits:
        print(f"   {path}:{line}  {detail}")

print(f"\nxaml files scanned: {len(XAML)}   findings: {len(findings)}")
print("A finding is a question, not a verdict. Confirm each against the file, then the live run.")
sys.exit(0)
