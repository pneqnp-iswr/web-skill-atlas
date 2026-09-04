# QRAFIG development skill system

A complete, drop-in Claude Code skill pack for **[pneqnp-iswr/qrafig](https://github.com/pneqnp-iswr/qrafig)** —
29 project skills, a task router, and a compact project-instructions bootstrap, all grounded in that
repository's own README, ADRs, status ledger and implementation.

It lives here in `web-skill-atlas` because this session was scoped to develop and push on this
repository's branch only. **It is written for the QRAFIG repository's root**, and installing it is one
command.

## What is here

```
qrafig/
├── CLAUDE.md                          → QRAFIG repo root: bootstrap + routing + non-negotiables
├── .claude/skills/<29 skills>/SKILL.md → QRAFIG repo root: the skills themselves
│   └── qrafig-desktop-wpf/scripts/xaml_audit.py
├── docs/ai/skills.md                  → registry: what each skill owns, triggers, dependencies
├── docs/ai/sources.md                 → source manifest: original / reused / adapted / rejected
├── docs/ai/routing-eval.md            → 96 prompts with expected routing, plus negative cases
└── install.sh                         → copies the four into a QRAFIG checkout
```

## Install into the QRAFIG repository

```bash
# from a checkout of this repository, with a QRAFIG checkout beside it
./qrafig/install.sh --dry-run /path/to/qrafig     # see exactly what would be written
./qrafig/install.sh /path/to/qrafig               # write it
```

The script refuses to overwrite an existing `CLAUDE.md` unless you pass `--force`, and it never
deletes anything. After installing, commit the result in the QRAFIG repository and start a session at
its root; Claude Code loads `CLAUDE.md` automatically and `.claude/skills/` becomes available.

Try it with:

```
/qrafig-router  Продолжи QRAFIG. Разберись что следующим нужно сделать, реализуй нормально и всё проверь.
```

## How it is meant to work

| | |
| --- | --- |
| **Always in context** | `CLAUDE.md` only — ~140 lines: source-of-truth order, the non-negotiable invariants, the gate commands, a one-line-per-skill index, and the conflict-resolution order. |
| **Entry point** | `/qrafig-router` decomposes a request into lanes (API, persistence, finance, POS, offline, inventory, purchasing, customers, reporting, authorization, tenancy, appsec, concurrency, outbox, storage, desktop, performance, diagnostics, site) and loads only those skills. |
| **On demand** | The other 26 skills load when their lane is active. A skill body costs nothing until it is used. |
| **Deliberately isolated** | A marketing-site task loads `qrafig-site` and nothing else. |

Each skill follows one shape: **when to use → read first → invariants → procedure → failure modes →
verification → do not → related skills.** Volatile numbers (test counts, migration counts, local
schema version) are *not* hard-coded — the skills tell the agent to read them from
`docs/implementation-status.md`, so the pack does not go stale as the project moves.

## What it is grounded in

Everything traces to the QRAFIG repository: 207 ADRs, a 3 600-line status ledger, the roadmap's global
engineering contract, the client save policy, and the implementation and tests themselves. Where a
canonical external skill adds framework depth — official .NET, Testcontainers, PostgreSQL,
idempotency, Next.js — it is **referenced by URL, never vendored**, and `docs/ai/sources.md` records
the author, licence, and any QRAFIG override that takes precedence over it.

Three families of external material were **rejected on purpose** and the reasons are recorded:
WinUI/WPF-migration skills (QRAFIG chose WPF deliberately), MVVM-toolkit-based WPF skills (QRAFIG's
view models must stay free of a UI framework), and CRDT/last-write-wins sync skills (QRAFIG is
server-authoritative with an operation log).

## Verifying the pack itself

```bash
python3 qrafig/validate_pack.py                      # frontmatter, names, links, staleness
python3 qrafig/.claude/skills/qrafig-desktop-wpf/scripts/xaml_audit.py /path/to/qrafig
```
