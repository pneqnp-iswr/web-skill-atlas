---
name: qrafig-authorization
description: Decide and enforce who may do what in QRAFIG — permission codes rather than role names, effective permissions computed from roles, graded policy limits, POS current authority versus historical attribution, the employee lifecycle (suspend, terminate, reassign, PIN), protected system and OWNER roles, and the tests that prove stale authority is refused. Use when adding or changing any authorized route, touching roles or employees, or auditing authorization.
when_to_use: New or changed endpoint authorization, role and permission work, employee lifecycle, POS eligibility and approval, "security audit of authorization", stale-token questions.
---

# Authorization in QRAFIG

Two rules underpin everything here, and both are load-bearing:

1. **Authorize by permission code, not by role name** (ADR-0022). Endpoints name
   `organization.manage`, `products.view`, `finance.approve`. The mapping from a caller's standing to
   a permission set lives in one place.
2. **A token proves the past; current authority is read now** (ADR-0126). A signed claim is evidence
   about the instant it was minted, never about the instant the command arrives.

## Read first

- `backend/src/Qrafig.Application/Organizations/OrganizationContext.cs` — `Require`,
  `RequireWritable`, `RequireOwner`, and `EmployeePolicy`.
- `backend/src/Qrafig.Application/Common/PermissionCodes.cs` and `PermissionCatalog.cs`.
- `backend/src/Qrafig.Application/Sales/CurrentPosAuthority.cs` and `PosActorResolver.cs` — the two
  and only two producers of a POS actor.
- `backend/src/Qrafig.Application/Sales/PosCapabilities.cs`, `PosEligibility.cs`.
- Tests: `EffectivePermissionTests`, `RoleTests`, `EmployeeTests`, `EmployeeConcurrencyTests`,
  `PosAuthorityTests`, `PurchasingAuthorizationTests`.
- ADRs: 0021, 0022, 0024, 0025, 0026, 0042, 0045, 0046, 0126, 0133, 0152, 0158, 0174, 0205, 0206, 0207.

## How authority is composed

- An employee holds **roles**; a role holds **permission codes**. The effective set is the **union**
  over the caller's active employee record's roles, computed per request and cached in
  `OrganizationContext`. Nothing denormalises a permission set onto an employee, so editing a role
  changes what every holder can do immediately (ADR-0024).
- **Graded limits** — POS login, discount ceiling, return approval, cost-price visibility — live on
  the role beside the codes and combine by taking the **most permissive** value across the caller's
  roles. A manager who also cashiers keeps the manager's ceiling.
- **The owner bypasses role resolution entirely** and holds every permission, including ones added in
  later releases. A member with no employee record yet falls back to the membership-derived baseline.
- Changing a caller's own roles invalidates their cached context, so a later check in the same
  request cannot read a stale set.

## Composing authorities

Authority is often a **conjunction**, and getting the conjunction wrong is a real defect class here:

- Purchasing composes an inventory operation with financial control (ADR-0158). Drafting and
  approving spend are different authorities.
- Approving a stocktake takes ordinary inventory authority **and** the elevated capability (ADR-0152).
- Customer money takes Finance authority; giving it up takes approval (ADR-0174).
- `canLoginAtPos` as shown to a person is the conjunction of **PIN set, employee status and role
  flag** — not the role flag alone. Reading the role flag as the answer tells a suspended cashier
  that no role of theirs may sign in, which is false and unhelpful.
- An `OWNER` role **can** sign in at a till. Do not assume otherwise.
- The server refuses Suspend and Record-leaving on your **own** card; the client must not offer them.

## POS: current authority vs historical attribution

| | Question | Answered by | Producer |
| --- | --- | --- | --- |
| **Current authority** | may this device and this person create work *now*? | the database, re-read at the moment of the command | `CurrentPosAuthority` → `PosCommandSource.DirectOnline` |
| **Historical attribution** | who was standing at this till when this was captured? | the operation, bounded by who could plausibly have been there | `PosActorResolver` → `PosCommandSource.SynchronizedCapture` |

`CurrentPosAuthority` re-reads, in order: the **device** (exists, right organization, right location,
currently `Active`, recovery flag refused) then the **employee** (present, `Active`, still assigned to
*this device's* location, still holding a role with `canLoginAtPos`) then the **special capability**
where one applies (approving a return reads `CanApproveReturns` live).

Suspended, terminated, unassigned and role-stripped all answer **identically** with
`POS_LOGIN_NOT_PERMITTED` — a differentiated message turns the till into a staff directory.
"Identified and not permitted to approve" stays a separate answer
(`RETURN_APPROVAL_NOT_PERMITTED`), which leaks nothing because the person already proved who they are.

**Synchronized operations deliberately do not check any of that.** A cashier who rang a sale, lost
the line and was suspended before the till reconnected still rang that sale; refusing it destroys the
only record that money changed hands. It lands, carries an `EMPLOYEE_NOT_ACTIVE` warning, and is
attributed to the person who rang it (ADR-0056, ADR-0126).

**Provenance is carried on `PosActor.Source`, never inferred** from a null id or a warning string.
Never add a status filter inside `PosCapabilities`: composed with a `DirectOnline` actor it *is* a
current-authority check, and composed with a `SynchronizedCapture` actor it is the historical rule.

## Client-side authority

The Desktop client **renders** the server's decisions and computes none of its own. Hiding a control
is a courtesy to the user, never a boundary (ADR-0042, ADR-0109). Every privileged call still goes to
the server and must survive being refused there. The client mirrors permission and feature code
strings rather than referencing the server assembly; `MirroredContractTests` is what makes that copy
safe. The summary endpoint describes the authority the endpoints enforce, including operational
policy the client cannot derive (ADR-0133).

## Employee lifecycle traps

- **Five saves that were silently last-write-wins** — the card, role assignment, shop scope, a role's
  policy and a role's permission set. Every save must name the version it was composed against
  (ADR-0205).
- **Claiming an employee number, creating a role code and deleting a role** each race a unique index;
  claim inside the inserting section and translate the named constraint.
- **Delete-versus-assign** must contend on the *same* key. Keying one side by code and the other by
  id means the two sections never meet, and `employee_roles` cascades take the assignment silently.
- **A plan ceiling checked before the insert** lets simultaneous hires all find room; check inside the
  gate that grants it (ADR-0206).
- A PIN is written but never read back (ADR-0207); the server requires exactly six digits.
- System roles and the OWNER role are protected differently (ADR-0026).

## Verification

For every authorized route: a **positive** case, a **missing-permission 403**, a **non-member 404**
(never 403 — see `qrafig-tenancy`), and a **cross-tenant** case. For POS routes add a **stale
authority** case: mint a token, change the underlying state, and prove the command is refused. For
approval paths add an **approve-races-reject** case.

## Do not

- Do not branch on role name, membership type or `IsOwner` in an endpoint. Name a permission.
- Do not treat "requires an authenticated user" as an authorization decision.
- Do not add a status filter to `PosCapabilities`.
- Do not refuse a synchronized offline operation because the employee is no longer active.
- Do not derive permissions on the client.
- Do not differentiate refusal messages at a till.
- Do not add a permission code without adding it to `PermissionCatalog` and to the client mirror if a
  client branches on it.

## Related skills

`qrafig-tenancy` (isolation and 404-over-403) · `qrafig-appsec` (tokens, hashing, secrets) ·
`qrafig-pos-domain` · `qrafig-offline-sync` · `qrafig-api-endpoints` · `qrafig-concurrency`.
