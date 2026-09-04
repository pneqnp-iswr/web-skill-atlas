---
name: qrafig-customers-privacy
description: QRAFIG's customer domain and its privacy obligations — anonymization that is never deletion and keeps the financial history, the bounded one-document privacy export, customer debt serialized by its subject, loyalty points as an append-only ledger, gift certificates as bearer instruments with readable codes, a sale that points at a customer rather than snapshotting a name, and what leaves the system. Use for customers, groups, contacts, notes, debt, loyalty, certificates, erasure, export or any personal data.
when_to_use: Customer records, groups, contacts, notes, debt and repayment, loyalty points, gift certificates, anonymization or erasure, data-subject export, PII handling, customer on a sale or at a till.
---

# Customers and personal data

## Read first

- `backend/src/Qrafig.Application/Customers/`, `backend/src/Qrafig.Api/Endpoints/CustomerEndpoints.cs`.
- Desktop: `CustomersViewModel`, `CustomerRegisterViewModel`, `CustomerDebtViewModel`,
  `CustomerLoyaltyViewModel`, `GiftCertificatesViewModel`, `CustomersView.xaml`.
- Tests: `CustomerTests`, `CustomerConcurrencyTests`, `CustomerContractTests`, `CustomerExportTests`,
  `DataRequestTests`; Desktop `CustomersWorkspaceTests`, `PosTillCustomerTests`,
  `PosCustomerLookupTests`, `CustomersVerticalSliceTests`.
- ADRs 0062, 0063, 0170 – 0192.

## Privacy

**Erasing a customer is anonymization, never deletion** (ADR-0063). The financial history stays —
a business must still be able to explain its books — while the identity is destroyed.

**Anonymization removes the free text, not only the fields** (ADR-0183). A note, a contact line or a
comment holds identity just as surely as a name column. Anonymization is **refused while money is
owed**.

**The privacy export is one complete document, bounded by refusal** (ADR-0192, superseding ADR-0188):

- `GET /organizations/{id}/customers/{id}/export`, taking `customers.manage`.
- A released ceiling of 25 000 records, **counted before any row loads**, enforced by **refusal**
  (`409 CUSTOMER_EXPORT_TOO_LARGE`) rather than truncation. A truncated document that looks complete
  is the failure being prevented.
- It is **complete** where the paged endpoints truncate — the points ledger comes back whole.
- It **names what it leaves out** and tells the truth about it.
- It carries **no** `rowVersion`, `moneyAccountId`, tender id or credential — asserted against the raw
  response as quoted JSON keys, so a future section cannot smuggle one back.
- An already-erased customer exports its **privacy state** and its **retained financial history**.
- Never-enrolled is not the same fact as enrolled-with-nothing: an untouched customer's lists are
  **empty rather than absent**, and loyalty and group are `null`.

Deliberately **not** routed through the organization-wide `data-requests/export`, whose Phase 19
worker does not exist.

## Domain rules

| | |
| --- | --- |
| **Save** | a customer or group save **names the version it was composed against** (ADR-0170). |
| **Codes** | a customer or group code is **claimed inside the section that inserts it** (ADR-0171). |
| **Contacts** | one primary contact per customer, **in the database** (ADR-0172). |
| **Debt** | a shared customer balance is **serialized by its subject, not by the drawer** (ADR-0173). Customer money takes Finance authority; giving it up takes approval (ADR-0174). Debt is visible to the customer desk, and history **names its shop** (ADR-0176). |
| **Groups** | a retired group **stops classifying and stays readable** (ADR-0175). |
| **Singletons** | a lazily seeded singleton is seeded **inside a section** (ADR-0177). |
| **Sales** | a sale **points at its customer and never snapshots their name** (ADR-0184). `sale.completed` carries the customer, and **only** the customer (ADR-0178). |
| **Certificates** | a certificate **records what backs its value** (ADR-0179); its **code is claimed** and its balance **serialized by the instrument** (ADR-0180); codes are **stored readable** (ADR-0062) because a bearer instrument has to be readable to be spent; a cancellation reason **does not overwrite the issue note** (ADR-0181). Only certificates **issued to** a customer appear in their export — a bearer instrument belongs to whoever holds the code. |
| **Classification** | every Customers mutation is **classified before it is given a key** (ADR-0182). |
| **Loyalty** | an append-only points ledger. Changing the loyalty rate moves what a balance is **worth** and rewrites nothing in the ledger. |
| **Offline** | Customers Backoffice is **online only**, with nowhere to wait (ADR-0185). At the till, credit / points / certificate are **tenders**, each refused **by the command** with the line down rather than merely by a disabled button. |
| **Held carts** | a held cart may carry an **identity, never an authority** (ADR-0186). |

A sale rung during an outage **keeps its customer** through the durable path and accrues **once** on
synchronization. A return **unwinds** the debt, points and certificate value it created.

## Handling personal data anywhere in QRAFIG

1. **Minimize what travels.** Outbox payloads, webhooks, notifications and exports carry the versioned
   contract, not the entity, and no unneeded PII.
2. **Log ids, not people.**
3. **Scope everything.** One customer's export must contain no row belonging to their neighbour and
   none belonging to another business — assert it.
4. **Prefer refusal to truncation** for any bounded read.
5. **Do not invent a deletion path.** Anonymization is the mechanism.

## Verification

`CustomerConcurrencyTests` (write it as a reproduction — the released implementation failed it: two
tills both sold 7 000 on account to a customer limited to 10 000 and both answered `201`);
`CustomerExportTests` for any export change; a cross-tenant assertion; Desktop workspace tests and
`PosTillCustomerTests` for tender behaviour; **and a live smoke** for a Customers UI change.

## Do not

- Do not delete a customer.
- Do not anonymize while money is owed.
- Do not leave free text behind on anonymization.
- Do not truncate an export.
- Do not put a credential, tender id, `rowVersion` or account id into an export.
- Do not snapshot a customer's name onto a sale.
- Do not cache customer data locally on the client.
- Do not treat a disabled button as a refusal for a tender.

## Related skills

`qrafig-appsec` · `qrafig-tenancy` · `qrafig-money-finance` · `qrafig-pos-domain` ·
`qrafig-storage` (export delivery) · `qrafig-concurrency`.
