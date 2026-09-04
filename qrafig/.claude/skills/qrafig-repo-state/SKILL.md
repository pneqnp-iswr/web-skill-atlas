---
name: qrafig-repo-state
description: Establish what QRAFIG actually is right now before changing it — read the session handoff, navigate the 3600-line status ledger and the 200-plus ADRs efficiently, find the decisions that govern an area, recognise a closed claim that must not be reopened, and resolve disagreements between documentation and code. Use at the start of every QRAFIG task, and especially for open-ended requests such as "continue development", "work out what to do next", or "what is the state of module X".
when_to_use: Continuation requests, "what is done", "what is next", locating an ADR, deciding whether a module claim is closed, or whenever documentation and implementation appear to disagree.
---

# Reading QRAFIG's current state

QRAFIG documents itself unusually well and unusually verbosely. The failure mode here is not missing
information — it is reading the wrong 400 kilobytes, or reading a stale header and believing it.

## Read first, in this order

1. `docs/implementation-status.md` → **`## Session handoff`** (starts around line 60). This table is
   the single freshest statement in the repository:
   - *Last completed task* / *Previous completed task* — what is finished, in detail.
   - *Current failing command* — the honest state of the gates.
   - *Next concrete task* — what the next session is supposed to do.
   - *Planned next Desktop slice* — plus any **defect carried forward**, which is real work someone
     deliberately left.
2. `docs/implementation-status.md` → `## Phase status` table — phase-by-phase `done` / `partial`.
3. `docs/implementation-status.md` → `## Completion criteria` (near the end) — the per-claim verdicts,
   including which Functional Alphas are closed and what each explicitly excludes.
4. `README.md` — the runnable commands and the operational contracts.
5. `docs/api-roadmap.md` §§ *Canonical source hierarchy*, *Global engineering contract*,
   *Cross-client Definition of Done*.

**The header block of the status ledger can lag the handoff table.** Both are updated by hand, and
the handoff is updated more often. When the header says one thing and the handoff row another, the
handoff row is current — and saying so in your report is useful, not pedantic.

## Navigating the ledger without reading all of it

```bash
grep -n '^#\{1,3\} ' docs/implementation-status.md        # section map, ~30 lines
sed -n '<start>,<end>p' docs/implementation-status.md      # read only the section you need
```

Useful anchors: `## Phase status`, `## Endpoint inventory`, `## Migration history`,
`## Test inventory`, `## QRAFIG Desktop — status`, `## Completion criteria`, `## SITE-SYNC FACTS`.

`## SITE-SYNC FACTS — <MODULE>` blocks are *data for the public site*: what is available now, what is
planned and not shipped, what the currency and security truth is. They are the most compact honest
summary of a finished module and are worth reading before you describe one.

## Finding the decisions that govern an area

```bash
grep -n '^## ADR-' docs/architecture-decisions.md                 # full index of titles
grep -n '^## ADR-' docs/architecture-decisions.md | grep -i shift # by topic
grep -n 'ADR-0129' docs/architecture-decisions.md README.md docs/implementation-status.md
grep -rn 'ADR-0129' backend/src desktop/src                       # where it is honoured in code
```

ADR titles are full sentences and are searchable by concept ("lock", "currency", "offline",
"idempot", "projection", "cursor", "claim"). Read the ADR **and** anything it supersedes or corrects —
several later records amend earlier ones (for example ADR-0038 corrects ADR-0035 and ADR-0036, and
ADR-0192 supersedes ADR-0188). The numbering is append-only, so a number never changes meaning.

Code comments cite ADR numbers. `grep -rn 'ADR-0' <file>` on any implementation file tells you which
decisions that file is carrying.

## Closed claims

The ledger marks whole modules **complete** — POS, Warehouse, Purchasing, Customers, Finance and
Employees Functional Alpha at the time of writing. A closed claim means:

- it was audited workflow by workflow and driven through the real `QRAFIG.exe`;
- its exclusions are deliberate and listed ("deliberately outside the boundary and **not** claimed");
- **it must not be reopened** as a side effect of other work.

Before starting, check whether your task lies inside one. If it does and the user did not ask you to
reopen it, say so and either scope the work outside the claim, or ask — this is one of the few
genuine product decisions the repository cannot settle for you. A defect explicitly *carried forward*
in the handoff is the exception: it is already named as outstanding work.

Equally, do not start a backend phase that the handoff tells you not to start. "Phase 19 remains
partial" is not an invitation.

## When documentation and code disagree

1. **Establish the fact from the implementation**, not from prose. Read the code and the tests.
2. **Do not invent a reconciliation.** If the roadmap describes an endpoint the tree does not have,
   the endpoint does not exist.
3. **Record the divergence** in your report, precisely: file, line, what each says.
4. **Correct documentation only when the correction is proved** by what you read, and prefer
   correcting the ledger (which claims to be authoritative about implementation) over rewriting an
   ADR (which is append-only history).
5. Never "fix" an ADR by editing it. Supersede it with a new one — see `qrafig-architecture`.

Known live examples of the pattern, useful as calibration:

- `docs/api-roadmap.md` names `QRAFIG_PRODUCT_BIBLE_v1.0.md` as the product source of truth; no file
  of that name is in the tree. The nearest artifacts are `О ПРОЕКТЕ` and `Каким Должен стать QRafig.md`.
- The status ledger's header block and its handoff table can describe different "last" work.

## Continuation requests

"Continue QRAFIG / work out what is next / carry on from the current state" resolves to exactly this:

1. Read the handoff. The *Next concrete task* is the task.
2. Read what that task says is **out of scope** — the handoff is explicit about deliberately unbuilt
   areas, and about which modules must not be reopened.
3. Route it through `/qrafig-router` as if the user had typed it.
4. Implement, test, and update the ledger **from evidence** — the handoff row, the phase status, the
   test counts, the migration list, the completion criteria — never from intention.

## Verification — updating the ledger when you finish

Update `docs/implementation-status.md` only with facts you produced:

- move the previous *Last completed task* down to *Previous completed task*, and write the new one;
- set *Current failing command* to the truth, including "none";
- write the next concrete task;
- update the counts (tests, migrations, local schema) **from the run you actually did**, and say which
  platform it ran on;
- add a `## SITE-SYNC FACTS — <MODULE>` block when a module reached a claimable state.

If you could not run a gate, the ledger must say so. A ledger that overstates is worse than no ledger.

## Do not

- Do not read `docs/architecture-decisions.md` or `docs/implementation-status.md` end to end. Grep the
  headings, then read ranges.
- Do not treat `docs/api-roadmap.md` as evidence of delivery. It is a plan.
- Do not treat a directory name as a description of what a module does.
- Do not restart a delivered phase or reopen a closed Functional Alpha unasked.
- Do not edit an ADR in place.

## Related skills

`qrafig-router` · `qrafig-architecture` (writing the ADR your change owes) · `qrafig-verification`
(what "done" means) · `qrafig-diagnostics` (when the state is "something is broken and nobody knows what").
