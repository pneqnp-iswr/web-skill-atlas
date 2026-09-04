---
name: qrafig-appsec
description: QRAFIG application security — JWT and refresh-token rotation with reuse detection, Argon2id password and PIN verifiers, the asymmetrically signed offline entitlement, device activation credentials shown once, Windows DPAPI credential blobs, API keys as hashed delegations, signed webhook callbacks, expiring signed storage links, rate limiting, secure headers, secrets handling, PII and log redaction, and the dependency vulnerability gate. Use for any credential, token, hash, signature, secret, PII or logging change, and for security audits.
when_to_use: Tokens, sign-in, PINs, device credentials, entitlements, API keys, webhooks, signed URLs, rate limits, secrets, logging and PII, dependency advisories, "security audit".
---

# QRAFIG application security

## Read first

- `backend/src/Qrafig.Infrastructure/Security/` — `JwtTokenService`, `Argon2PasswordHasher`,
  `EntitlementSigner`.
- `backend/src/Qrafig.Api/Security/SecurityHeadersMiddleware.cs`,
  `backend/src/Qrafig.Api/RateLimiting/RateLimitingSetup.cs`.
- `desktop/src/Qrafig.Desktop.Infrastructure/Security/` — `ProtectedSessionStore`,
  `ProtectedDeviceCredentialStore`, `Argon2PinVerifier`.
- Tests: `AccountSecurityTests`, `RefreshTokenTests`, `ProfileAndSessionTests`,
  `RateLimitAndHeaderTests`, `PosDeviceTests`, `OfflinePinVerifierTests`, `OfflineColdStartTests`.
- ADRs 0010, 0012, 0013, 0025, 0042, 0043, 0044, 0045, 0046, 0084, 0088, 0092, 0098, 0126, 0131.

## The primitives, and why each is what it is

| Concern | QRAFIG's choice |
| --- | --- |
| **Passwords and PINs** | Argon2id (`Konscious.Security.Cryptography.Argon2`), encoded as `argon2id$v=19$m=…,t=…,p=…$salt$hash`, verified with `CryptographicOperations.FixedTimeEquals`. Do not change the parameters without a migration plan for stored hashes. |
| **Access tokens** | Short-lived JWT, HMAC-signed. Not individually revocable — cutting refresh families is what withdraws access. |
| **Refresh tokens** | Rotated, with **families and reuse detection** (ADR-0012). Replaying a rotated token revokes the family. |
| **Offline entitlement** | **ECDSA P-256 (ES256)**, asymmetric on purpose: the verifying key ships inside every POS binary, so a symmetric key would let anyone who unpacks the client mint an unlimited licence. Public key at `GET /api/v1/pos/entitlement-key`. `Entitlement:PrivateKeyPem` is required in Production and startup refuses without it (ADR-0044). |
| **Device identity** | A till authenticates **as itself**, not as a person (ADR-0042); tenant identity derives from the device credential (ADR-0013). Activation codes and device credentials are shown **once** (ADR-0043). |
| **PIN verifiers at the till** | Deliberately shipped, on their own endpoint `GET /api/v1/pos/offline-auth`, bounded by scope (this device's location only), eligibility (active, PIN set, `canLoginAtPos`), and cost (Argon2id work factor). The general bootstrap carries **no** PIN material (ADR-0046). |
| **Client credential storage** | Windows **DPAPI** (`ProtectedData`, `CurrentUser`), written via a temporary file so a crash cannot truncate the blob. `device.bin`, `offline-auth.bin`, `session.bin` under `%LOCALAPPDATA%\QRAFIG\Desktop`. |
| **API keys** | A **delegation**, stored hashed, identified by a prefix (ADR-0088). |
| **Provider callbacks** | Only a **signed** provider callback activates anything (ADR-0084); the development billing provider verifies a real HMAC and fails closed without a secret. |
| **Storage links** | The key is the server's, the bucket is private, and **every link expires** (ADR-0098). A signed link is a credential. |
| **Support access** | Reasoned, expiring and visible to the business (ADR-0092); every Control action is audited (ADR-0093). |

## Secrets and configuration (ADR-0010)

Configuration order is `appsettings.json` → `appsettings.{Environment}.json` → user-secrets →
environment variables. **The application never parses `.env`** — Compose reads it and passes values
in. Locally use `dotnet user-secrets`; in containers and production supply the same keys as
environment variables with `__` as the separator (`Jwt__SigningKey`, `ConnectionStrings__Postgres`).

Never commit a secret. Never add a real credential to `appsettings.Development.json` — the values
there grant access to nothing outside the developer's machine, and that is the property to preserve.

## Redaction and logging

- Never log a token, refresh token, PIN, Argon2 hash, device credential, activation code, API key,
  webhook secret or **signed storage URL**.
- Outbox faults log the message id, worker id, exception **type** and a redacted summary bounded to
  500 characters — never the exception object.
- Personal data belongs in the record, not in the log line. Log ids.
- An error message must not confirm that an entity exists in another tenant, and a POS refusal must
  not differentiate between suspended, terminated, unassigned and role-stripped.

## The security questions for any change

1. **Where does this credential live, who can read it, and how does it expire?**
2. **What happens if it is replayed?** (Refresh reuse, idempotency key reuse, webhook replay,
   duplicate sync push, a re-sent signed URL.)
3. **What happens if it is brute-forced?** Rate limits are partitioned device → user → IP with a
   tighter auth policy; account lockout exists. A six-digit PIN's protection is the Argon2 cost.
4. **What does the error say?** Refuse without teaching.
5. **Could organization A reach B?** — hand to `qrafig-tenancy`.
6. **Is authority re-read, or trusted from a claim?** — hand to `qrafig-authorization`.
7. **Does anything sensitive reach a log, an export, an outbox payload or a webhook?**

## Dependency advisories

```bash
dotnet list package --vulnerable --include-transitive     # must report none
```

Transitive pinning is enabled centrally, so a transitive advisory is fixed by one `PackageVersion`
entry in `Directory.Packages.props` — the repository already does this for `SSH.NET`, reached through
Testcontainers' Docker client. Record why the pin is there in a comment beside it.

## Failure modes

- Reusing the JWT signing key to sign entitlements, which hands out a minting key with every client.
- Relaxing Argon2 parameters "for test speed" in a way that reaches production configuration.
- Logging a request body that contains a PIN or a token.
- Returning a differentiated POS refusal that turns the till into a staff directory.
- Treating a client-side check as a boundary.
- Adding a new endpoint that returns a permanent object URL instead of an expiring signed link.
- Storing an API key in plaintext because "we need to show it again" — it is shown once.
- Catching a signature-verification failure and proceeding.

## Verification

Backend integration security tests including negative and replay cases; rate-limit and header tests;
`dotnet list package --vulnerable --include-transitive`; and, for anything touching DPAPI, a Windows
run — the DPAPI baseline on Windows is **zero** failures, so a DPAPI failure there is a real regression.

## Do not

- Do not reuse the JWT signing key to sign entitlements — that hands out a minting key with every client.
- Do not weaken Argon2 parameters, even "for tests", in a way that can reach production configuration.
- Do not log a token, PIN, hash, credential, activation code or signed URL.
- Do not differentiate a POS refusal message.
- Do not treat a client-side check as a boundary.
- Do not return a permanent object URL instead of an expiring signed link.
- Do not store an API key in plaintext.
- Do not proceed after a signature-verification failure.
- Do not commit a secret, or parse `.env` in application code.

## Related skills

`qrafig-authorization` · `qrafig-tenancy` · `qrafig-storage` · `qrafig-outbox-jobs` ·
`qrafig-observability` (redaction in logs and traces) · `qrafig-offline-sync`.
