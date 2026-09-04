---
name: qrafig-desktop-live-smoke
description: The live QRAFIG.exe validation gate — when driving the real Windows executable is mandatory rather than optional, how to set up an isolated server and a clean profile, the exact flow lettering and evidence convention QRAFIG uses, the state transitions that must each be entered by every path that can reach them, and how to record the result in the ledger. Use before claiming any Desktop workspace or XAML change complete.
when_to_use: Before claiming a Desktop change or workspace complete; when a defect appears only in the running application; when writing or updating the evidence for a Functional Alpha claim.
---

# The live `QRAFIG.exe` smoke

> **Compiling markup is evidence about names, not about rendering.** A Desktop workspace is not claimed
> complete until the shipped `QRAFIG.exe` has been driven through it on Windows (ADR-0191).

Nine of eleven defects found in one live run were invisible to every test in this repository, because
nothing but WPF resolves a `StaticResource`, applies a `DataContext`, evaluates a `Trigger`, measures
layout, or asks a command whether it may execute.

## Read first

- `README.md` §§ *QRAFIG Desktop*, *Build and run*, *Launching a mode*.
- `docs/implementation-status.md` → `## QRAFIG Desktop — status`, the handoff row's live-run defect
  list, and the `## Completion criteria` rows for the claims already proved this way.
- ADR-0191, and `qrafig-desktop-wpf` for the defect classes to look for.

## When it is mandatory

Any change that touches:

- a `.xaml` file, a view, a resource dictionary, a converter, a style or a template;
- navigation, the shell, an access state, or a workspace's lifecycle;
- a command's `CanExecute`, or the property notifications that drive one;
- anything a person sees, reads or presses.

## When it is not

A backend-only change with no client contract movement. But if the change moved a **contract the
client mirrors** — a permission code, a feature code, an error code, or a wire field — `MirroredContractTests`
is the tripwire and the smoke is back on the list.

## Setup

```bash
dotnet build desktop/src/Qrafig.Desktop            # 0 warnings, 0 errors
dotnet run  --project desktop/src/Qrafig.Desktop   # or run the built QRAFIG.exe
# executable: desktop/src/Qrafig.Desktop/bin/Debug/net10.0-windows/QRAFIG.exe
```

- **Windows.** DPAPI has no Linux implementation and the smoke cannot run there at all.
- **A live isolated API**, not a shared one — `docker compose up postgres redis -d` then
  `dotnet run --project backend/src/Qrafig.Api`. Never drive the smoke against anyone else's data.
- **A clean local profile** for a first-launch flow: `%LOCALAPPDATA%\QRAFIG\Desktop` holds
  `device.bin`, `offline-auth.bin`, `session.bin` and the local SQLite database. Move it aside rather
  than deleting it if you may need to compare.
- **Modes**: `QRAFIG.exe`, `--mode=pos`, `--mode=warehouse`, `--mode=purchasing`, `--mode=backoffice`
  (also `--mode pos`, `/mode:pos`, `-m pos`, case-insensitive). The argument chooses a starting
  workspace; it grants nothing.
- **Two display conditions at minimum**: 150% scaling, and a **1280×720 DIP laptop layout**. That is
  the bar the repository's existing claims were proved at, and it is where clipping shows.

## What to drive

Write the flows as lettered scenarios (**Flow A**, **Flow B**, …) and record the *observed figures*,
not "it worked". The repository's own evidence reads like
`Flow A completed CNT-000001 with G-1 40 + 0 = 40 and W-1 40 − 6 = 34, both counted exactly, and no
adjustment` — a number somebody can check, from a screen somebody looked at.

Cover, for the surface you changed:

| Class | What to enter |
| --- | --- |
| **First launch** | a clean profile: activation or sign-in, and the empty state of every list. An empty state is a screen, not an absence. |
| **The happy path** | end to end, to a committed result, and read the result back from a fresh load. |
| **Every section** | open each section of a workspace and confirm **only that one** is visible. Sections rendering at once is the `DataContext` shadowing defect. |
| **Every command** | press each button. A permanently disabled button is the `CanExecute` defect and is invisible to tests. |
| **The tab strip** | confirm the selected tab is actually highlighted. |
| **Editor open and close** | including cancel, and re-open — a form that says something is wrong before anything is typed is a defect. |
| **Navigation** | into the workspace, away, and back. Then to a second workspace and back again. |
| **Online → offline → online** | pull the server down **while standing in the workspace**, not only before entering it. A workspace that becomes unreachable *where it stands* is a distinct path, and it went completely blank once. Then restore and confirm it recovers **without** pressing Refresh. |
| **Refusals** | a permission refusal, an entitlement lock, an offline notice and a not-built page must each be the *right one* of the four (see `qrafig-desktop-workspace`). |
| **Restart** | close normally and relaunch: the session and device restore, and `PRAGMA user_version` on the local database reads the expected schema. |
| **Organization switch** | nothing carries across. |
| **Layout** | at 150% and at 1280×720: no clipped column, no truncated currency code, no text cut in half, no unexplained empty half-screen. |
| **Keyboard** | complete the primary workflow without a mouse; check focus after a dialog closes. |

For a POS surface add: activation, PIN sign-in, offline sign-in, shift open, cart, tender, durable
checkout, receipt and reprint, return with and without approval, void, cash in/out, held cart claim,
X and Z, an outage mid-sale, and a **crash and restart** with the operation still queued.

## Verification — the evidence a run produces

The run produces four things:

1. **The lettered flows and their observed figures.**
2. **A clean application log** — the Desktop rolling file log under the local profile. On Windows the
   DPAPI baseline is **zero** failures, so any DPAPI error is a real regression.
3. **A list of defects found**, each with the file and the reason it was invisible to the tests.
4. **A ledger update**: the handoff row, and the completion-criteria row for the claim, naming the
   flows, the scaling conditions and the log.

## If you cannot run it

Say so explicitly — "no Windows host, so the live smoke did not run" — and state what is therefore
unproven. Then do everything you can that is not the smoke: build with
`-p:EnableWindowsTargeting=true`, run the static XAML audit
(`python .claude/skills/qrafig-desktop-wpf/scripts/xaml_audit.py .`), run the Desktop view-model
suite, and re-read the diff against the defect classes in `qrafig-desktop-wpf`.

**Do not mark a Desktop workspace complete on that basis.** An unproven claim in the ledger is worse
than an honest gap.

## Do not

- Do not substitute more headless tests for the smoke; they cannot see this class of defect.
- Do not drive it against a shared or production API.
- Do not run only the happy path.
- Do not check a state only through the path you happened to build.
- Do not report "looks fine" — report figures, sections, commands and the log.

## Related skills

`qrafig-desktop-wpf` (the defect classes and the audit) · `qrafig-desktop-workspace` ·
`qrafig-verification` · `qrafig-repo-state` (recording the result) · `qrafig-pos-domain`.
