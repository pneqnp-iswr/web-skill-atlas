# Database gaps — 2026-08-27

The pass materially improved relational, document, key-value, graph, vector, time-series, distributed SQL, ORM, migration, indexing, and observability coverage. The gaps below remain because no qualifying standalone published skill passed canonical and factual review.

## Provider-Neutral Database Deadlock Diagnosis

No technically reliable standalone published skill survived review; accepted engine packs discuss deadlocks only as a subsection.

Potential value: High: a wait-for-graph, victim, retry, and lock-order workflow would prevent misleading permanent-hang diagnoses.

Notes: Keep engine-specific detection and victim semantics explicit; do not invent a published skill from documentation.

## Optimistic Concurrency Token Audit

Broad concurrency skills were found, but no focused cross-ORM procedure covers version columns, SQL Server rowversion, HTTP ETags, JPA @Version, EF tokens, and DynamoDB conditional writes.

Potential value: High: catches silent lost updates across APIs and ORM layers.

Notes: The accepted Database Concurrency Audit gives partial coverage, so this opportunity is for a narrower implementation-and-test workflow.

## Distributed Lock Fencing Audit

Redis and general database sources discuss locks, but no qualifying published skill validates monotonically increasing fencing tokens and stale-holder rejection.

Potential value: High: prevents stale lock holders from mutating protected resources after lease expiry.

Notes: Do not reduce the workflow to Redlock acquisition; downstream resource enforcement is the missing core.

## Advisory Lock Correctness Review

Published PostgreSQL skills mention advisory locks, but no standalone workflow covers key design, session versus transaction scope, leak prevention, pooling, and observability.

Potential value: Medium-high: advisory-lock misuse can serialize unrelated tenants or leak locks through pooled sessions.

Notes: Engine semantics differ; a future workflow should branch explicitly.

## Firebase Realtime Database Data Modeling

Official Firebase agent skills cover Firestore and SQL Connect, but no dedicated Realtime Database skill was verified.

Potential value: Medium: denormalized fan-out writes, rules, offline behavior, and query limits differ materially from Firestore.

Notes: Ordinary Firebase documentation is not a published skill and remains only source material.

## Cloudflare D1 Production Migration Safety

Official D1 guidance is nested reference material, while the two standalone community candidates failed safety and currency review.

Potential value: High: remote migration ordering, partial failure, bindings, backups, and rollback need a safe executable contract.

Notes: Do not split Cloudflare reference pages into invented catalog entries.

## SQLite WAL and Busy-Timeout Operations

Turso and SQLite/D1 audit skills provide partial coverage, but no accurate standalone SQLite concurrency and recovery workflow passed review.

Potential value: High for embedded and edge applications that mis-handle writer contention and checkpoint growth.

Notes: Reject unqualified throughput multipliers and obsolete sqlite-vss recommendations.

## Provider-Neutral Cassandra Data Modeling

Amazon Keyspaces supplies strong Cassandra-compatible guidance, but no provider-neutral Cassandra skill was verified.

Potential value: Medium-high: query-first modeling, partition sizing, tombstones, and consistency levels are easy to misapply.

Notes: Keep Keyspaces-specific compatibility separate from portable Cassandra semantics.

## ScyllaDB Web Data-Layer Review

No credible ScyllaDB-specific published skill survived organization, registry, code, and gap searches.

Potential value: Medium: shard-aware drivers, partition sizing, and workload-specific differences deserve explicit treatment.

Notes: scylla-cluster-tests results are project testing infrastructure, not reusable application skills.

## Mongoose Schema and Query Review

Official MongoDB skills are driver and database focused; no credible Mongoose-specific reusable skill was verified.

Potential value: Medium-high: populate behavior, lean reads, middleware, discriminators, and transaction sessions create ORM-specific risks.

Notes: Do not relabel generic MongoDB guidance as Mongoose expertise.

## KeyDB Compatibility and Migration Review

Redis coverage is deep, but no trustworthy KeyDB-specific published skill was found.

Potential value: Medium: compatibility, active replication, and multi-threaded behavior should not be inferred from Redis alone.

Notes: A future published workflow should clearly scope supported KeyDB versions.

## Cross-Engine Restore Verification

Engine and provider skills discuss backup and restore, but no provider-neutral skill verifies logical correctness, constraints, sequences, permissions, RPO, and application smoke after restore.

Potential value: High: backup success without restore correctness is a common false assurance.

Notes: The accepted MariaDB and Neon/PostgreSQL sources are engine-specific, not this cross-engine audit.

## ORM-specific gaps

No strong standalone canonical skills survived for Mongoose, standalone Alembic, jOOQ, Diesel, SeaORM, SQLx, Knex, or Kysely. Cross-ORM coverage exists in Safe SQL Migrations and Relational Schema Antipattern Review, but it is not a substitute for engine- and API-specific workflows.

## Search limitations

GitHub shared search rate limits caused transient failures that were retried or covered through repository trees and independent searches. Elastic, OpenSearch, and Pinecone candidates remain explicitly deferred where full-body review did not reach the same bar as accepted entries.
