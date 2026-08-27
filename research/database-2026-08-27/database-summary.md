# Database deep-research summary — 2026-08-27

## Outcome

| Metric | Value |
| --- | --- |
| Concrete candidates reviewed | 362 |
| Generated query variants | 1024 |
| Named query families / research waves | 57 / 16 |
| Directly logged search queries/attempts | 137 |
| New accepted after dedupe | 161 |
| Duplicates/mirrors | 80 |
| Rejected/deferred | 101 |
| Derived opportunities | 12 |
| Databases category before → after | 20 → 166 |
| Total atlas before → after | 658 → 819 |
| Verified new / partially verified new | 161 / 0 |
| Metadata / canonical-source corrections | 14 / 3 |
| Unique accepted repositories | 37 |
| New / updated / removed source records | 30 / 9 / 1 |

All 1,024 query variants are stored in `database-query-matrix.json`; they are explicitly marked generated-not-executed. Candidate counts include only file-level triage, accepted entries, documented duplicates/rejects, and the 20-record baseline audit.

## Quality distribution

| Score band | New skills |
| --- | --- |
| 95-100 | 2 |
| 90-94 | 75 |
| 85-89 | 67 |
| 80-84 | 12 |
| 70-79 | 5 |
| below-70 | 0 |

Scores use the full calibrated range. Scores at 95 or above are reserved for exceptional, deeply procedural sources; unknown licenses remain source-link-only with `mirror_allowed: false`.

## Database-engine coverage

| Engine/family | New entries mentioning it |
| --- | --- |
| PostgreSQL | 51 |
| MySQL | 27 |
| MariaDB | 10 |
| SQLite | 9 |
| libSQL/Turso | 2 |
| Cloudflare D1 | 3 |
| SQL Server | 8 |
| Oracle | 10 |
| MongoDB | 12 |
| Redis/Valkey | 5 |
| DynamoDB | 3 |
| Firestore | 1 |
| Cassandra/Keyspaces | 2 |
| Neo4j | 9 |
| Qdrant | 14 |
| Milvus | 2 |
| StarRocks | 10 |
| Hologres | 10 |
| TimescaleDB | 2 |
| InfluxDB | 1 |
| Snowflake | 1 |
| Cosmos DB | 1 |
| OpenSearch | 1 |
| YugabyteDB | 2 |
| Vitess | 1 |
| Convex | 4 |

## ORM and migration-tool coverage

| ORM/tool | New entries mentioning it |
| --- | --- |
| Prisma | 7 |
| Drizzle | 5 |
| Django ORM | 3 |
| SQLAlchemy/Alembic | 2 |
| EF Core | 3 |
| Hibernate/JPA | 1 |
| Eloquent | 5 |
| ActiveRecord | 3 |
| GORM | 1 |
| TypeORM | 2 |
| Sequelize | 2 |
| Knex | 1 |
| Flyway | 2 |
| Liquibase | 1 |
| Spring Data Neo4j | 1 |
| sqlc | 3 |

## Task-family coverage

| Task family | New entries |
| --- | --- |
| Query Optimization | 12 |
| Safe Migrations | 10 |
| Connection Management | 6 |
| Schema Design | 6 |
| Database Security | 4 |
| Vector Search | 4 |
| Distributed SQL | 3 |
| Observability | 3 |
| PostgreSQL | 3 |
| Backend Testing | 2 |
| Data Access | 2 |
| Database Migration | 2 |
| Distributed Database Operations | 2 |
| Document Databases | 2 |
| DynamoDB Data Access | 2 |
| Hybrid Search | 2 |
| Indexing | 2 |
| Multi-tenancy | 2 |
| ORM Mapping | 2 |
| Performance Diagnosis | 2 |
| Prisma | 2 |
| Schema Visualization | 2 |
| Time-Series | 2 |
| Vector Store Integration | 2 |
| Backup & Restore | 1 |
| Capacity Planning | 1 |
| Convex | 1 |
| Cypher | 1 |
| Data Ingestion | 1 |
| Data Integrity | 1 |

## Top 50 new entries

| # | Name | Score | Classification | Canonical source |
| --- | --- | --- | --- | --- |
| 1 | Amazon DynamoDB Data-Layer Design | 96 | Databases / DynamoDB | https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/specialized-skills/database-skills/amazon-dynamodb/SKILL.md |
| 2 | Neon PostgreSQL Best Practices | 95 | Databases / PostgreSQL | https://github.com/neondatabase/postgres-skills/blob/main/skills/postgres-best-practices/SKILL.md |
| 3 | Aurora DSQL Safe Data Engineering | 94 | Databases / Distributed SQL | https://github.com/aws/agent-toolkit-for-aws/blob/main/skills/specialized-skills/database-skills/aurora-dsql/SKILL.md |
| 4 | MariaDB Query Optimization | 94 | Databases / Query Optimization | https://github.com/MariaDB/skills/blob/main/mariadb-query-optimization/SKILL.md |
| 5 | MongoDB Schema Design | 94 | Databases / Schema Design | https://github.com/mongodb/agent-skills/blob/main/skills/mongodb-schema-design/SKILL.md |
| 6 | Neo4j Cypher Engineering | 94 | Databases / Cypher | https://github.com/neo4j-contrib/neo4j-skills/blob/main/neo4j-cypher-skill/SKILL.md |
| 7 | Neo4j Graph Modeling | 94 | Databases / Graph Modeling | https://github.com/neo4j-contrib/neo4j-skills/blob/main/neo4j-modeling-skill/SKILL.md |
| 8 | Neo4j Query Tuning | 94 | Databases / Query Optimization | https://github.com/neo4j-contrib/neo4j-skills/blob/main/neo4j-query-tuning-skill/SKILL.md |
| 9 | Safe SQL Migrations | 94 | Databases / Safe Migrations | https://github.com/sigistry/marketplace/blob/main/plugins/sql-safety-net/skills/safe-migrations/SKILL.md |
| 10 | Database Migration Safety Audit | 93 | Databases / Safe Migrations | https://github.com/Hainrixz/claude-db/blob/main/skills/db-migration-safety/SKILL.md |
| 11 | MongoDB Query Optimization | 93 | Databases / Query Optimization | https://github.com/mongodb/agent-skills/blob/main/skills/mongodb-query-optimizer/SKILL.md |
| 12 | Neo4j Vector Index Engineering | 93 | Databases / Vector Search | https://github.com/neo4j-contrib/neo4j-skills/blob/main/neo4j-vector-index-skill/SKILL.md |
| 13 | Qdrant Model Migration | 93 | Databases / Model Migrations | https://github.com/qdrant/skills/blob/main/skills/qdrant-model-migration/SKILL.md |
| 14 | Qdrant Multi-Tenancy | 93 | Databases / Multi-tenancy | https://github.com/qdrant/skills/blob/main/skills/qdrant-multitenancy/SKILL.md |
| 15 | Relational Schema Antipattern Review | 93 | Databases / ORM Mapping | https://github.com/sigistry/marketplace/blob/main/plugins/sql-safety-net/skills/schema-antipatterns/SKILL.md |
| 16 | Review Oracle-to-PostgreSQL Migration | 93 | Databases / Safe Migrations | https://github.com/github/awesome-copilot/blob/main/skills/reviewing-oracle-to-postgres-migration/SKILL.md |
| 17 | StarRocks Query Diagnosis | 93 | Databases / Query Optimization | https://github.com/StarRocks/starrocks-debug-skills/blob/main/query/SKILL.md |
| 18 | Azure Cosmos DB NoSQL Data Modeling | 92 | Databases / Document Databases | https://github.com/github/awesome-copilot/blob/main/skills/cosmosdb-datamodeling/SKILL.md |
| 19 | Cloud Firestore Database Operations | 92 | Databases / Firestore | https://github.com/firebase/agent-skills/blob/main/skills/firebase-firestore/SKILL.md |
| 20 | Database Connection Pool Audit | 92 | Databases / Connection Management | https://github.com/Hainrixz/claude-db/blob/main/skills/db-connection-pooling/SKILL.md |
| 21 | Database Indexing Audit | 92 | Databases / Indexing | https://github.com/Hainrixz/claude-db/blob/main/skills/db-indexing/SKILL.md |
| 22 | Database Query Pattern Audit | 92 | Databases / Query Optimization | https://github.com/Hainrixz/claude-db/blob/main/skills/db-query-patterns/SKILL.md |
| 23 | Hologres Query Optimization | 92 | Databases / Query Optimization | https://github.com/aliyun/hologres-ai-plugins/blob/main/agent-skills/skills/hologres-query-optimizer/SKILL.md |
| 24 | MariaDB Replication and High Availability | 92 | Databases / Replication & HA | https://github.com/MariaDB/skills/blob/main/mariadb-replication-and-ha/SKILL.md |
| 25 | Migrate .NET Oracle Data Access to PostgreSQL | 92 | Databases / Data Access | https://github.com/github/awesome-copilot/blob/main/skills/migrating-oracle-to-postgres-data-access-code/SKILL.md |
| 26 | MongoDB Connection Management | 92 | Databases / Connection Management | https://github.com/mongodb/agent-skills/blob/main/skills/mongodb-connection/SKILL.md |
| 27 | MongoDB Search and AI | 92 | Databases / Search & Vector | https://github.com/mongodb/agent-skills/blob/main/skills/mongodb-search-and-ai/SKILL.md |
| 28 | Neo4j Cypher and Driver Migration | 92 | Databases / Database Migrations | https://github.com/neo4j-contrib/neo4j-skills/blob/main/neo4j-migration-skill/SKILL.md |
| 29 | PlanetScale MySQL Engineering | 92 | Databases / MySQL | https://github.com/planetscale/database-skills/blob/main/skills/mysql/SKILL.md |
| 30 | Qdrant Capacity Sizing | 92 | Databases / Capacity Planning | https://github.com/qdrant/skills/blob/main/skills/qdrant-sizing/SKILL.md |
| 31 | Qdrant Indexing Performance Optimization | 92 | Databases / Indexing Performance | https://github.com/qdrant/skills/blob/main/skills/qdrant-performance-optimization/indexing-performance-optimization/SKILL.md |
| 32 | Qdrant Relevance Feedback | 92 | Databases / Relevance Feedback | https://github.com/qdrant/skills/blob/main/skills/qdrant-search-quality/search-strategies/relevance-feedback/SKILL.md |
| 33 | Qdrant Search Quality Diagnosis | 92 | Databases / Search Quality | https://github.com/qdrant/skills/blob/main/skills/qdrant-search-quality/diagnosis/SKILL.md |
| 34 | Qdrant Search Speed Optimization | 92 | Databases / Query Optimization | https://github.com/qdrant/skills/blob/main/skills/qdrant-performance-optimization/search-speed-optimization/SKILL.md |
| 35 | Qdrant Sliding Time-Window Retention | 92 | Databases / Retention | https://github.com/qdrant/skills/blob/main/skills/qdrant-scaling/scaling-data-volume/sliding-time-window/SKILL.md |
| 36 | Redis Core Data Modeling | 92 | Databases / Redis Data Modeling | https://github.com/redis/agent-skills/blob/main/skills/redis-core/SKILL.md |
| 37 | Spring Data Neo4j | 92 | Databases / ORM & Data Access | https://github.com/neo4j-contrib/neo4j-skills/blob/main/neo4j-spring-data-skill/SKILL.md |
| 38 | SQL EXPLAIN Interpreter | 92 | Databases / Query Optimization | https://github.com/sigistry/marketplace/blob/main/plugins/sql-safety-net/skills/explain-interpreter/SKILL.md |
| 39 | SQL to ER Diagram Workflow | 92 | Databases / Schema Visualization | https://github.com/ystemsrx/sql_to_ER/blob/master/skills/sql2er/SKILL.md |
| 40 | StarRocks Compaction Diagnosis | 92 | Databases / Storage & Compaction | https://github.com/StarRocks/starrocks-debug-skills/blob/main/compaction/SKILL.md |
| 41 | StarRocks Materialized View Diagnosis | 92 | Databases / Materialized Views | https://github.com/StarRocks/starrocks-debug-skills/blob/main/materialized-view/SKILL.md |
| 42 | StarRocks Tablet Diagnosis | 92 | Databases / Storage & Replication | https://github.com/StarRocks/starrocks-debug-skills/blob/main/tablet/SKILL.md |
| 43 | YugabyteDB YSQL Engineering | 92 | Databases / Distributed SQL | https://github.com/yugabyte/yugabytedb-skills/blob/main/skills/ysql/SKILL.md |
| 44 | Database Concurrency Audit | 91 | Databases / Transactions & Concurrency | https://github.com/Hainrixz/claude-db/blob/main/skills/db-concurrency/SKILL.md |
| 45 | Database Multi-Tenancy Isolation Audit | 91 | Security / Multi-tenancy | https://github.com/Hainrixz/claude-db/blob/main/skills/db-multitenancy/SKILL.md |
| 46 | Database Security and Access Audit | 91 | Security / Database Security | https://github.com/Hainrixz/claude-db/blob/main/skills/db-security-access/SKILL.md |
| 47 | Database Storage and Bloat Audit | 91 | Databases / Maintenance | https://github.com/Hainrixz/claude-db/blob/main/skills/db-storage-bloat/SKILL.md |
| 48 | Django Data-Access Performance Review | 91 | Databases / Django ORM | https://github.com/getsentry/skills/blob/main/skills/django-perf-review/SKILL.md |
| 49 | Hologres Schema Generation | 91 | Databases / Schema Design | https://github.com/aliyun/hologres-ai-plugins/blob/main/agent-skills/skills/hologres-schema-generator/SKILL.md |
| 50 | Milvus Vector Database Engineering | 91 | Databases / Vector Databases | https://github.com/zilliztech/milvus-skill/blob/main/SKILL.md |

## Canonical and metadata corrections

| ID | Entry | Fields corrected |
| --- | --- | --- |
| webskill-0094 | Vercel Storage | description, frameworks, languages, license, mirror_allowed, source_detail, source_url, tools |
| webskill-0139 | Supabase Postgres Best Practices | description, frameworks, languages, mirror_allowed, source_detail, source_url, tools |
| webskill-0222 | Prisma Client API | description, frameworks, languages, quality_score, tools |
| webskill-0223 | Prisma Database Setup | description, frameworks, languages, quality_score, tools |
| webskill-0224 | Prisma CLI Database Workflows | frameworks, languages, quality_score, tools |
| webskill-0225 | Prisma Postgres | description, frameworks, languages, quality_score, tools |
| webskill-0226 | Prisma Upgrade v6 to v7 | description, frameworks, languages, quality_score, tools |
| webskill-0227 | Convex | description, frameworks, languages, license, mirror_allowed, quality_score, source_detail, source_url, status, tools |
| webskill-0637 | Redis Clustering | languages, subcategory, tools |
| webskill-0638 | Redis Connections | languages, subcategory, tools |
| webskill-0639 | Redis Observability | category, subcategory, tools |
| webskill-0640 | Redis Search | languages, quality_score, subcategory, tools |
| webskill-0642 | Redis Semantic Cache | languages, quality_score, tools |
| webskill-0648 | Firebase SQL Connect | frameworks, languages, name, quality_score, subcategory, tools |

The most consequential corrections replace Vercel Storage, Supabase Postgres Best Practices, and Convex repository/tree locators with exact canonical blobs; upgrade Convex to verified with its observed Apache-2.0 license; clarify all five Prisma workflows; move Redis Observability into Databases; and align Firebase Data Connect with the current Firebase SQL Connect naming while preserving its stable slug.

## Best long-tail additions

- Keyset Pagination; Database Queues and Outbox; MariaDB System-Versioned Tables; Qdrant Sliding Time-Window Retention; Hologres BSI Profile Analysis; PostgreSQL Row-Level Security Audit; SQL to ER Diagram Workflow; Qdrant Model Migration; MariaDB Backup to Object Storage; and StarRocks Tablet Diagnosis.

## Remaining gaps

The largest focused gaps are provider-neutral deadlock diagnosis, optimistic concurrency tokens, fencing, advisory-lock correctness, Firebase Realtime Database, safe D1 migrations, SQLite WAL operations, provider-neutral Cassandra, ScyllaDB, Mongoose, KeyDB, and cross-engine restore verification. See `database-gaps.md` and `database-derived-workflow-opportunities.json`.

## Validation

Local verification passed:

- `python scripts/validate.py`: 819 skills, 25 taxonomy categories, 819 unique slugs.
- `python scripts/deduplicate.py`: 0 candidates at the repository threshold; a separate manual cross-category similarity review retained only deliberately independent engine- or task-specific files.
- `python scripts/generate.py`: 819 visible skills, 674 verified, 145 partially verified, 166 in Databases, and 267 source records.
- Second generator run produced the identical tracked diff hash `c3936731e31f2cb491292bccde7d57251f9c2cae`.
- `python scripts/validate_issue_forms.py`: 2 forms validated.
- `python scripts/scan_secrets.py`: clean.
- GitHub tree audit: 37 accepted repositories, 161 exact source locators checked, 0 missing.
- Current-branch audit: 36 repository heads still matched the recorded snapshot. `event4u-app/agent-config` advanced after inspection, but all six accepted skill blob hashes are unchanged at its current head.
- License audit: 35 repositories matched their declared SPDX license; the two repositories with no detected license remain `unknown`, source-link-only, and `mirror_allowed: false`. The AGPL entry is also source-link-only.
- Query matrix: 1,024 variants, 1,024 unique, SHA-256 `275c4717181b41d2012f6f88709083a855bd11eb6b36b6679999f552a8dfd3be`.

Push and GitHub Actions evidence is recorded after publication.
