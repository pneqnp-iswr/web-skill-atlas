---
name: qrafig-storage
description: Work with QRAFIG's object storage — the three-call upload with capacity reserved before the bytes, server-owned keys in a private bucket, expiring signed links treated as credentials, checksums and content type measured from the object rather than accepted from the client, the expiry, deletion and reconciliation passes, and the local and S3-compatible providers. Use for product images, finance attachments, report exports, migration attachments, quotas or any file path.
when_to_use: File upload or download, presigned URLs, S3 or R2 configuration, storage quotas, orphaned objects, product images, attachments, export delivery.
---

# Object storage in QRAFIG

Files — product photographs, finance attachments, report exports, legacy migration attachments — live
in object storage and **never in PostgreSQL**. Two real providers chosen by configuration, plus a
development provider that is also real (ADR-0101).

| Setting | Meaning |
| --- | --- |
| `Storage:Provider` | `local` (default) or `s3` |
| `Storage:Local:Root` | where the local provider writes; defaults under the system temp path |
| `Storage:Bucket`, `Storage:AccessKeyId`, `Storage:SecretAccessKey` | required when the provider is `s3`; **startup fails without them** |
| `Storage:ServiceUrl` | the S3-compatible endpoint; empty means AWS, resolved from `Storage:Region` |
| `Storage:ForcePathStyle` | `true` for Cloudflare R2, MinIO and most self-hosted gateways |

## Read first

- `README.md` § *Object storage*.
- `backend/src/Qrafig.Infrastructure/Storage/LocalObjectStorage.cs`, `S3ObjectStorage.cs`.
- `backend/src/Qrafig.Application/Storage/*`, `backend/src/Qrafig.Api/Endpoints/StorageEndpoints.cs`.
- Tests: `StorageTests`, `StorageHelpers`.
- ADRs 0097, 0098, 0099, 0100, 0101.

## Uploading is three calls, not one

```
POST   /api/v1/organizations/{id}/files/uploads       # reserve capacity, get a signed URL
PUT    <the signed URL>                               # the bytes go straight to the bucket
POST   /api/v1/organizations/{id}/files/{fileId}/finalize
```

- **Capacity is taken at the reservation**, under a tenant advisory lock (ADR-0097), so a plan with no
  room refuses **before** twenty megabytes are sent rather than after.
- The bytes go **straight to the bucket**, so uploads never compete with the API instance ringing a
  shop's sales.
- **Finalization reads the object back** and takes its size, its SHA-256 and its leading bytes from
  that pass. The checksum is **measured, not accepted**, and bytes that do not begin the way the
  declared content type must are refused (ADR-0099). Nothing about an upload is believed until the
  bytes are measured.

## Links are credentials

**Buckets are private and there is no permanent URL.** Reading a file means asking for a link, which
expires in minutes. The key is the **server's** — never built from a client-supplied name.

> A signed link is a credential: **never log one**, never put one in an outbox payload, a webhook body,
> a notification, an export or an error message.

## The three passes

| Job | What it does |
| --- | --- |
| `storage.expiry` | releases capacity held by uploads that never finished |
| `storage.deletion` | removes the bytes of files marked for deletion |
| `storage.reconciliation` | compares record and bucket nightly, **corrects sizes and reports everything else** (ADR-0100) |

Each is also invokable at `POST /api/v1/organizations/{id}/files/maintenance/…`. Reconciliation does
not delete on a mismatch — it reports, because a bucket disagreeing with the record is a question for a
person.

## Delete behaviours

References **to** a stored object (`product_images`, `finance_attachments`) are **Restrict**, not
Cascade: detaching is what releases a file, and cascading would leave bytes in the bucket that nothing
in the database remembers. `stored_objects` cascades with the organization. `ux_stored_objects_key` is
**global rather than per tenant**, so two tenants can never address one object.

A nullable `stored_object_id` on a legacy attachment stays nullable, with a **partial** unique index
`WHERE stored_object_id IS NOT NULL` — an attachment made before the subsystem existed genuinely has
no object, and backfilling one would mean inventing a record for bytes QRAFIG never saw.

## Verification — adding a file-carrying feature

1. Reserve → upload → finalize. Do not invent a single-call path.
2. Server-generated, tenant-scoped key. Never trust a client filename for the key.
3. Declare the content type, and let finalization **prove** it from the leading bytes.
4. Return an expiring link, never a permanent URL.
5. Decide the delete behaviour deliberately and say why.
6. Make sure the three passes know about the new reference; an object nothing releases is a leak.
7. Confirm the quota path — capacity reserved before the bytes.
8. Cross-tenant test: organization A cannot address, read or delete organization B's object.

## Do not

- Do not store file bytes in PostgreSQL.
- Do not return or log a signed URL anywhere it could be persisted.
- Do not accept a client-supplied checksum or content type as fact.
- Do not build a key from user input.
- Do not cascade a delete from a stored object's referrer.
- Do not delete on a reconciliation mismatch.
- Do not add an `s3` provider configuration without the startup validation that fails closed.

## Related skills

`qrafig-appsec` · `qrafig-outbox-jobs` (the passes are jobs) · `qrafig-tenancy` ·
`qrafig-efcore-migrations` (indexes and delete behaviours) · `qrafig-customers-privacy` (exports).
