---
name: qrafig-diagnostics
description: Find out what is actually broken in QRAFIG before changing anything — reproduce first, then triage by surface (API 500 or wrong answer, a Desktop screen that renders nothing or does nothing, a till that will not sync, a test that fails for environmental reasons, a defect that appears only when the real QRAFIG.exe runs). Covers the correlation trail, the outbox and job logs, WPF binding diagnostics, the local database and queue, and how to tell an environment failure from a code failure. Use for "work out what is broken", an unexplained failure, or a bug report with no cause.
when_to_use: "Something is broken", an unexplained 500, a blank or dead screen, a stuck sync queue, mass test failures, a defect only visible at run time, a production incident.
---

# Diagnosing QRAFIG

**Reproduce before you change anything.** A fix without a reproduction is a guess, and the repository's
own precedent is that the reproduction *is* the deliverable: race tests were written to fail against
the released implementation before anything was fixed.

## Read first

- `docs/implementation-status.md` → the handoff's *Current failing command*, and the environment note.
- `README.md` § *Verification* and § *Background jobs*.
- The failing test, log line or screen — before any source file.
- ADRs 0018, 0020, 0094, 0115, 0129, 0191.

## Step 0 — is it the environment?

Several QRAFIG failures look like hundreds of code defects and are not:

| Symptom | Actually |
| --- | --- |
| ~900 integration tests fail at `RegisterAndLoginAsync` with `500` | a whole-solution `dotnet test` started ~50 container pairs and took the Docker daemon down. **Run the four projects separately.** |
| 37 Desktop failures, all `PlatformNotSupportedException` from `ProtectedData` | DPAPI has no Linux implementation. On Windows the baseline is **zero** — a DPAPI failure *there* is real. |
| WPF project will not build on Linux | needs `-p:EnableWindowsTargeting=true`. |
| Testcontainers cannot pull an image | a restricted network; `mirror.gcr.io` and `TESTCONTAINERS_RYUK_DISABLED=true`. |
| A job reports `skipped` | another replica holds the advisory lock. That is the mechanism working. |

Rule out the environment before writing a line of code, and say which it was in your report.

## Step 1 — name the surface

| Surface | Start at |
| --- | --- |
| API answered wrongly or 500 | the `X-Correlation-Id` / `X-Trace-Id` on the response, or in the Problem Details body |
| Desktop screen renders nothing / the previous workspace stays | `qrafig-desktop-wpf` — a `StaticResource` that does not exist, or a style whose `TargetType` is wrong. Both throw inside `InitializeComponent()`, and the binding engine swallows it |
| Desktop control renders but does nothing | a command that never re-asks `CanExecute` (ADR-0190), or a control bound to nothing |
| Desktop sections all visible at once | a `DataContext` override shadowing a sibling `Visibility` binding |
| Till will not sync | the local queue and cursor, then the push outcome, then the change feed |
| Money is wrong | the ledger, then the projection — reconciliation refuses with `LEDGER_OUT_OF_BALANCE` when they disagree, and that is a defect signal, not a counting error |
| Stock is wrong | movements are the truth; the balance is a projection. Sum the movements |
| Event never arrived | the outbox: status, attempts, lease, dead letters |
| It only happens in the real application | `qrafig-desktop-live-smoke` |

## Step 2 — the trails

**API.** Every response carries `X-Correlation-Id` and `X-Trace-Id`, and every log line of that request
carries both in its scope. Filter by them first.

**Outbox.**

```
GET /api/v1/control/outbox/health           # backlog, oldest pending age, dead letters, throughput
GET /api/v1/control/outbox?status=dead_lettered
GET /api/v1/control/outbox/{messageId}      # the message and every attempt at it
```

**Jobs.** `GET /api/v1/control/jobs?job=…` — a run that died mid-flight is a `running` row with no
finish, not an absence.

**Desktop.** The rolling file log under `%LOCALAPPDATA%\QRAFIG\Desktop`. Binding failures do **not**
appear there — WPF writes them to the debugger's trace output. To surface one, raise the trace level on
the suspect binding:

```xml
xmlns:diag="clr-namespace:System.Diagnostics;assembly=WindowsBase"
<TextBlock Text="{Binding Total, diag:PresentationTraceSources.TraceLevel=High}" />
```

and read the WPF data-binding trace. Check the exact API against the WPF documentation for the
installed .NET before relying on a detail.

**Local database.** `PRAGMA user_version` gives the schema; the operation queue, `device_sequences`
and the cursor rows give the sync state. Stranded work is surfaced, never deleted — look for it.

## Step 3 — form a hypothesis that predicts something

A good hypothesis says what *else* must be true. "The binding is failing" predicts that the value is
default and that a trace line exists. "Two callers raced" predicts that two rows exist, or that one got
a `500` and the other a `201`. Check the prediction before you fix.

The QRAFIG-shaped hypotheses worth reaching for first:

- **Two clients did it at once.** See the race catalogue in `qrafig-concurrency`.
- **A pre-check was treated as a guarantee**, and the index refused the loser unhandled.
- **A projection and its source disagree** — balance vs ledger, stock vs movements, sync state vs
  operations.
- **Authority was read from a token instead of the database**, or the reverse: a synchronized operation
  was refused for authority reasons it should never be checked against.
- **A snapshot was assembled from several statements** and shows two figures that cannot both be true.
- **The client decided something it may not decide** — a permission, a price, a ceiling, a drawer.
- **The change feed cursor skipped a row** because it ordered by an insert-time sequence.
- **WPF resolved something at run time that the compiler never checked.**

## Step 4 — write the reproduction

Put it in the suite that can hold it (`qrafig-testing`). Confirm it **fails** against the current code.
For a race, fire independent clients simultaneously. For a durability question, kill the process. For a
rendering question, there is no test — that is the live smoke.

## Step 5 — fix the cause

- Do not widen a `catch` to make a `500` disappear; find what threw.
- Do not add a retry to hide a deadlock; fix the lock order.
- Do not relax an assertion, a permission or a bound to make a symptom go away.
- Do not "fix" documentation to match broken behaviour.
- Keep the fix minimal, and record the decision as an ADR if it constrains other modules.

## Step 6 — report

What you reproduced, how; the cause, with the file and line; the fix; the gates you ran and their
results; and the gates you could not run and why. If the cause is still unknown, say that plainly along
with what you ruled out — an honest "not found yet" is worth more than a plausible wrong answer.

## Verification

A diagnosis is finished when: the failure reproduces on demand, the reproduction lives in the suite
that can hold it (or is documented as un-testable and covered by the live smoke), the fix makes it
pass, the surrounding suites are still green, and the report says which gates ran and which did not.
An unreproduced fix is a guess with a commit message.

## Do not

- Do not change code before you have reproduced the failure.
- Do not widen a `catch`, add a retry, relax an assertion or raise a bound to make a symptom go away.
- Do not call a failure a flake without evidence — check the environment list above first.
- Do not "fix" documentation to match broken behaviour.
- Do not report a cause you have not demonstrated; an honest "not found yet" is worth more.
- Do not skip the reproduction because the fix looks obvious.

## Related skills

`qrafig-testing` · `qrafig-concurrency` · `qrafig-desktop-wpf` · `qrafig-desktop-live-smoke` ·
`qrafig-offline-sync` · `qrafig-observability` · `qrafig-repo-state` · `qrafig-verification`.
