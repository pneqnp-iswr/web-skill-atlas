# Database research log — 2026-08-27

This log records work actually performed. External repositories were treated as untrusted read-only research content; no upstream script was executed.

## Execution accounting

- Generated query variants: **1,024 unique variants**. They were generated as a coverage matrix, not executed as 1,024 searches.
- Explicitly enumerated specialist query families: **57**; required research waves executed: **16/16**.
- Directly logged search queries or attempts across independent agents: **137**. An interrupted rate-limited registry loop whose completed-attempt count was not preserved is excluded rather than estimated.
- skills.sh: 26 task/engine query families with top-100 windows (2,600 raw registry rows before dedupe). Raw rows were not counted as reviewed candidates.
- GitHub code search: 18 first-pass attempts plus 30 specialist executions/attempts; repository search: 19 first-pass queries plus 10 specialist families; web, multilingual, and registry discovery supplied the remaining directly logged attempts.
- Concrete candidate accounting: **362** = 161 accepted + 80 duplicates/mirrors + 101 rejected/deferred + 14 corrected existing + 6 unchanged baseline records.

## Waves

| Wave | Surface | Reviewed | Accepted | Duplicates | Rejected/deferred | Corrections |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Existing atlas baseline | 21 | 0 | 1 | 0 | 14 |
| 2 | Official database agent-skill repositories | 47 | 43 | 0 | 4 | 0 |
| 3 | skills.sh and registries | 31 | 24 | 0 | 7 | 0 |
| 4 | GitHub repository search | 0 | 0 | 0 | 0 | 0 |
| 5 | GitHub code search | 0 | 0 | 0 | 0 | 0 |
| 6 | Database vendor organizations | 39 | 18 | 2 | 19 | 0 |
| 7 | ORM and query-builder organizations | 14 | 12 | 2 | 0 | 0 |
| 8 | Cloud and database providers | 19 | 10 | 0 | 9 | 0 |
| 9 | Database performance specialists | 9 | 3 | 0 | 6 | 0 |
| 10 | Awesome lists and curated collections | 22 | 12 | 0 | 10 | 0 |
| 11 | Maintainer snowballing | 25 | 14 | 0 | 11 | 0 |
| 12 | Social and community discovery | 4 | 3 | 0 | 1 | 0 |
| 13 | Multilingual discovery | 25 | 10 | 0 | 15 | 0 |
| 14 | Long-tail database failures | 8 | 4 | 0 | 4 | 0 |
| 15 | Gap-driven second pass | 25 | 8 | 3 | 14 | 0 |
| 16 | Saturation, canonicalization, and dedupe audit | 73 | 0 | 72 | 1 | 0 |

### Wave 1: Existing atlas baseline

Inspected all 20 Databases-category records plus adjacent Redis, EF Core, Django, JPA, migration, and storage entries; 14 records warranted metadata corrections.

### Wave 2: Official database agent-skill repositories

Opened canonical official repositories for MongoDB, Qdrant, Redis, Neon, MariaDB, PlanetScale, Prisma, Neo4j Contrib, Turso, and YugabyteDB.

### Wave 3: skills.sh and registries

Ran 26 skills.sh database/task query families with top-100 windows; registry rows were discovery leads only and were never counted as reviewed candidates until canonical triage.

### Wave 4: GitHub repository search

Ran 29 repository-search queries across engines, databases, skills, ORM ecosystems, migrations, and query performance; raw result counts were not promoted into candidate totals.

### Wave 5: GitHub code search

Ran 30 authenticated code-search executions across engine and failure terms, including six rate-limit attempts that were retried; candidate counting began only after file-level triage.

### Wave 6: Database vendor organizations

Inspected vendor organizations and exact repository trees for database and vector engines; downstream plugin packaging was separated from canonical leaves.

### Wave 7: ORM and query-builder organizations

Searched Prisma, Drizzle, SQLAlchemy, Django ORM, EF Core, Hibernate, jOOQ, Eloquent, ActiveRecord, GORM, Diesel, SeaORM, SQLx, Knex, Kysely, and sqlc surfaces.

### Wave 8: Cloud and database providers

Reviewed AWS, Firebase, Vercel, Neon, Supabase, Turso, Azure-adjacent, and managed database workflows; provisioning-primary material was rejected.

### Wave 9: Database performance specialists

Inspected query-plan, indexing, PgBouncer, PostgreSQL, MariaDB, Grafana, and operational-performance specialists with a factual-correctness gate.

### Wave 10: Awesome lists and curated collections

Used GitHub Awesome Copilot and curated collections for discovery, then traced every accepted entry to a direct canonical blob and rejected defective helpers.

### Wave 11: Maintainer snowballing

Snowballed from maintainers and skill references into event4u, Sigistry, Convex, sql2er, and focused data-access repositories.

### Wave 12: Social and community discovery

Used publicly indexed community results only; no account-gated social interaction was attempted and no skill was accepted solely from a social claim.

### Wave 13: Multilingual discovery

Executed Chinese, Japanese, Korean, Russian, Spanish, Portuguese, French, and German searches. The unique accepted addition was the ten-skill official Hologres cluster; 12 Aliyun AIOps candidates remained deferred.

### Wave 14: Long-tail database failures

Targeted deadlocks, N+1, SKIP LOCKED, keyset pagination, backups, restore, bloat, pooling, migrations, and long-tail failure signatures.

### Wave 15: Gap-driven second pass

Re-ran targeted searches for underrepresented MySQL, SQLite, libSQL, D1, MongoDB, DynamoDB, Firestore, SQL Server, and ORM gaps.

### Wave 16: Saturation, canonicalization, and dedupe audit

Compared locators, names, descriptions, paths, source trees, and known adapter hashes; retained canonical leaves and documented every grouped mirror count.

## Multilingual and social limitations

Searches were executed in English, Chinese, Japanese, Korean, Russian, Spanish, Portuguese, French, and German. Chinese discovery uniquely added the ten accepted Hologres leaves and surfaced 12 Aliyun AIOps candidates that remained deferred for scope and license reasons. Japanese, Korean, Russian, Spanish, Portuguese, French, and German searches did not add a unique canonical accepted source after dedupe.

TikTok, Instagram, and X were not treated as exhaustive discovery surfaces because public indexing and account-gated access are incomplete. Publicly indexed community results were used only as leads; none became canonical evidence without an upstream file.

## Accepted-source snapshots

| Repository | Branch | Inspected SHA | Observed license | Author |
| --- | --- | --- | --- | --- |
| auralshin/coding-skills | main | 35766f5523b532a7d4dbfaa951fd74451abda7f0 | MIT | auralshin |
| github/awesome-copilot | main | 634b92f887487fc61cddc2f61d77830e09e8f589 | MIT | GitHub community |
| aws/agent-toolkit-for-aws | main | 53a736826aa511004609478b03a9d00e11ee4991 | Apache-2.0 | AWS |
| capcom6/mariadb-backup-s3 | master | aededbc352fb4f324fdbd36fcb5f562453d4b80d | Apache-2.0 | Aleksandr Soloshenko |
| Hainrixz/claude-db | main | b50e44f131f00215aa14c4cd20d9506cefba65d6 | MIT | Enrique Rocha |
| waynesutton/convexskills | main | 8ef49c96675f760dd5569c0588c1abb04cd989dd | Apache-2.0 | waynesutton |
| davidondrej/skills | main | 3fd9bf6e1365389fa8f6c6844b614eac6a85c31e | MIT | David Ondrej |
| giuseppe-trisciuoglio/developer-kit | main | 50f0b945bd81ee1dac377f609871e63b732347fa | MIT | Giuseppe Trisciuoglio |
| event4u-app/agent-config | main | 460b6200786e8c544a53416631b34d78ab730667 | MIT | event4u-app |
| firebase/agent-skills | main | a0b4e143f40c1ebe05fe5f9a4787fecd4da8f478 | Apache-2.0 | Firebase |
| grafana/skills | main | 51d33e71e191b409bbd25fc7be2684c610d18166 | Apache-2.0 | Grafana |
| aliyun/hologres-ai-plugins | main | b635e6afb091b342a3f7a05692acfba339d9086a | Apache-2.0 | Alibaba Cloud Hologres |
| MariaDB/skills | main | 86623494f8051e766c973d35c1f07368c3b4c267 | MIT | MariaDB |
| zilliztech/milvus-skill | main | 7553e6c2b5940aef0f4a1aacc40d956745af0ac5 | Apache-2.0 | Zilliz |
| mizchi/skills | main | 7a0d72866a0bb3e9ac3e2768c328b09ba2bc40c4 | unknown | mizchi |
| mongodb/agent-skills | main | 6ebabd86ebdbe85f37082e9a7d37e18ebf6ebba0 | Apache-2.0 | MongoDB |
| neo4j-contrib/neo4j-skills | main | a9a5e783c506bcb17e7f415f24685b4f0df04069 | MIT | Neo4j Contrib |
| neondatabase/agent-skills | main | 46498bcde91c2d293bfe5e23614594991e46211e | Apache-2.0 | Neon |
| neondatabase/postgres-skills | main | 27fe45e0f71ea89a6eaf9ea4d2e4068957c81c26 | Apache-2.0 | Neon |
| neondatabase/ai-rules | main | 1ceaf89a4e0acfbaf152ac2e85d45afd55f49c0f | MIT | Neon |
| netdata/skills | master | ae650fc3766642f14e29892ab4fed607ac29d263 | Apache-2.0 | Netdata |
| planetscale/database-skills | main | af0ce0cfb65cca4cc21d18ca0d9cf270ca99d488 | MIT | PlanetScale |
| raunakjhawar/skills-for-postgres | main | 29d5e5c02ecb6d31f2e53a4556b09559b95da56e | MIT | raunakjhawar |
| prisma/skills | main | 808913c1dac11dc425631c2454f7fcb2d5ade5ca | MIT | Prisma |
| qdrant/skills | main | bcca2c2da1c00992038e83038e01791d468f943d | Apache-2.0 | Qdrant |
| redis/agent-skills | main | 172fb9effa139cd7432ac29a9ee81c45943e5a28 | MIT | Redis |
| ccheney/robust-skills | main | 23df06465a698aa4571da041da21fd4c5f58e618 | MIT | ccheney |
| sanjay3290/ai-skills | main | 361969210b1002034be70de60a041a25732b098a | Apache-2.0 | sanjay3290 |
| getsentry/skills | main | c2f99a5b04b4cd992ec3022d7c2c3e23e938d241 | Apache-2.0 | Sentry |
| sigistry/marketplace | main | 571bc2f550d72ae4a1fd5201710c5e7cccb66b2d | MIT | sigistry |
| ystemsrx/sql_to_ER | master | 92bd4478f83dab1b02a99dfd6cf6bea8a98ef1aa | AGPL-3.0 | ystemsrx |
| StarRocks/starrocks-debug-skills | main | 6237680f6798e2d6c90b94f4b5ba15e3f469cd93 | Apache-2.0 | StarRocks |
| supabase/agent-skills | main | 8331f910845103c08d51f6ca1d86ebb7d1f745e3 | MIT | Supabase |
| timescale/pg-aiguide | main | b4f11a45907af3abda0f79e784aff9a6d5eef468 | Apache-2.0 | TigerData / Timescale |
| TroyKelly/claude-skills | main | 38a2ecc528a0289b1027d31c96ea171811bb993c | unknown | Troy Kelly |
| TursoDatabase/agent-skills | main | 34ced52fd1bd32e802622126e299cfa886d68441 | MIT | Turso |
| upstash/redis-js | main | 1bec5669e36efbe88579c267f9dd287a4c63572a | MIT | Upstash |
| vercel/vercel-plugin | main | c4a1c4e2e16feefb1d9f2ad2a4a451abd0ae91c6 | Apache-2.0 | Vercel |
| yugabyte/yugabytedb-skills | main | 72e1c4e4a514835ab49bf6d6f8498faed06cc6c4 | Apache-2.0 | YugabyteDB |

## Saturation conclusion

The final broad and gap-driven searches increasingly returned existing atlas entries, plugin adapters, routing hubs, ordinary documentation, generic personas, mass-generated packs, or the same canonical files. Underrepresented engines received a second pass before stopping. Remaining gaps are recorded as derived opportunities rather than invented skills.

## Local verification evidence

- Atlas validation: 819 skills, 25 categories, 819 unique slugs.
- Repository dedupe: 0 candidates; manual high-similarity pairs were reviewed across all categories.
- Canonical locator audit: 37 repositories, 161 accepted files, 0 missing paths at the recorded SHAs.
- Current branch heads matched 36 recorded snapshots. The one advanced repository, `event4u-app/agent-config`, retained identical blob hashes for all six accepted skill files.
- License audit: 35 SPDX matches; `mizchi/skills` and `TroyKelly/claude-skills` remained `unknown` with mirroring disabled; the AGPL sql2er entry is source-link-only.
- Issue forms: 2 validated. Secret scan: clean.
- Deterministic generator replay: identical tracked diff hash `c3936731e31f2cb491292bccde7d57251f9c2cae` before and after replay.
