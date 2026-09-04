---
name: qrafig-tenancy
description: Keep QRAFIG's organizations and locations isolated — the single OrganizationContext choke point, 404 over 403 so tenants cannot be enumerated, scoping of queries, cursors, cache keys, background jobs, object-storage paths, exports, notifications and webhooks, and the negative tests that prove organization A cannot read or influence organization B. Use for every new or changed route, query, worker, cache or file path, and for any IDOR or cross-tenant review.
when_to_use: New or changed endpoint, query, background job, cache key, storage path or export; "can org A see org B", IDOR review, tenant isolation audit, location-scoping questions.
---

# Multi-tenancy in QRAFIG

One shared application and one shared PostgreSQL serve every tenant. Isolation is enforced by code,
not by deployment. It therefore has to be enforced in **one place**, and it is.

## The choke point (ADR-0021)

Every organization-scoped operation resolves an `OrganizationContext` through
`OrganizationContextResolver` — the only code that turns *(user, organization)* into an access
decision. It is scoped per request and caches its result, so several concerns can ask without
repeating the query.

```
RequireAsync(...)          → membership + permissions resolved
RequireWritableAsync(...)  → and the organization currently accepts writes
```

**There is no path that queries tenant data without one.** If you find yourself re-deriving
membership inside a service, stop: that is the defect the choke point exists to prevent.

## 404 over 403 — and when 403 is right

| Caller | Answer |
| --- | --- |
| Not an **active member** of the organization | `404 ORGANIZATION_NOT_FOUND` |
| A member, lacking the specific permission | `403 MISSING_PERMISSION` |

A `403` confirms an organization with that id exists, which lets an outsider enumerate tenants by
iterating identifiers. `403` is reserved for callers who *are* members, where the organization's
existence is already known to them.

Suspending or removing a member takes effect immediately because their refresh families are cut at
the same time. Access tokens are short-lived but not individually revocable, so cutting the refresh
families is what actually withdraws access.

## Everything that has to be scoped

Not just the obvious query. Walk this list for every change:

| Surface | The question |
| --- | --- |
| **Query** | is the organization id in the `WHERE`, on **every** joined table that carries one? |
| **Child by id** | is the child re-checked against the parent's organization, or only fetched by its own id? |
| **Cursor / pagination token** | can a cursor minted in org A be replayed in org B? |
| **Cache key** | does the key contain the organization (and the location, where the answer is per-location)? |
| **Background job** | does the sweep run per tenant, and does a per-tenant run stay inside its tenant? Control may sweep all — deliberately and audited. |
| **Object storage** | is the key server-generated and tenant-prefixed? Is the bucket private and the link expiring? |
| **Export / report** | does the document contain a row belonging to a neighbour or to another business? |
| **Notification** | is the audience derived from the permission holders **of that organization**? |
| **Webhook / outbox payload** | does the versioned contract carry only that tenant's data, and no credential or signed URL? |
| **Log line** | does it carry ids rather than personal data, and never a token or a signed link? |
| **Error message** | does a refusal reveal that an id exists in another tenant? |

**Location boundaries are a second axis.** An employee assigned to one shop must not act at another;
POS current authority re-reads the device's own location (ADR-0126); a store-scoped figure must say
which figures are not the store's (ADR-0194); a transfer is an instruction about shared stock and is
never captured offline (ADR-0149). Do not assume organization scoping implies location scoping.

## Read first

- `backend/src/Qrafig.Application/Organizations/OrganizationContext.cs`
- the nearest existing endpoint in the same module — the scoping pattern is uniform
- `backend/tests/Qrafig.IntegrationTests/MembershipTests.cs`, `OrganizationTests.cs`, and the
  cross-tenant cases inside each module's test file
- `CustomerExportTests` — the pattern for proving a document contains no neighbour's rows
- ADRs 0021, 0022, 0027, 0028, 0091, 0092, 0097, 0098, 0143.

## Verification

Every route that reads or writes tenant data owes a cross-tenant negative test. The shape:

```
create org A with data
create org B with a different owner
call B's client against A's identifiers
assert 404 (not 403, not 200-with-empty, not 500)
```

For documents and exports, assert against the **raw response body** that no identifier belonging to
the neighbour appears — `CustomerExportTests` checks quoted JSON keys so a future section cannot
smuggle one back. For jobs, assert a per-tenant run touched only its tenant.

"Requires an authenticated user" is not proof. "The query has a `WHERE organization_id`" is not proof
either — a joined table without one is the usual defect.

## Failure modes

- Fetching a child by its own id and never checking its parent's organization.
- A cache key without the tenant, so the second tenant gets the first one's answer.
- A background sweep that iterates all rows because it was written for Control and then reused.
- A cursor that encodes a raw primary key and is accepted from any tenant.
- A file path built from a client-supplied name rather than a server-generated key.
- A `403` where a `404` was owed, leaking that the organization exists.
- A report that scopes the top-level query and then joins an unscoped lookup table.
- An error message naming an entity from another tenant.

## Do not

- Do not add a second place that decides tenant access.
- Do not use a client-supplied organization id without resolving it.
- Do not return `403` to a non-member.
- Do not widen a query to "fix" an empty result without checking why it was empty.

## Related skills

`qrafig-authorization` · `qrafig-api-endpoints` · `qrafig-storage` · `qrafig-outbox-jobs` ·
`qrafig-reporting` · `qrafig-customers-privacy`.
