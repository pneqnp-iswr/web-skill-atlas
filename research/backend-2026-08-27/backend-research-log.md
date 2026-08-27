# Backend research log - 2026-08-27

## Scope and counting

This pass generated 600 unique query variants from 20 framework/technology terms x 15 task families x 2 file conventions. The generated matrix SHA-256 is `6c56f4b9246b4f8c840ea573c915e4d16f596960d1cca1427df75783184c0f5b`. This is explicitly a generated matrix, not a claim that 600 network searches were executed. Concrete candidate review counts only opened skill/rule/instruction files, inspected repository packs, duplicate adapter files, explicit no-skill official repository checks, and existing records corrected in place.

## Waves actually executed

1. Existing Backend/APIs/Security/Databases/Architecture/Testing/DevOps/Deployment/Performance baseline and dedupe-risk audit.
2. Thirty-two skills.sh query families covering frameworks and long-tail failure modes.
3. GitHub repository/tree/code searches for SKILL.md, hidden .agents/.agent/.ai trees, rules, references, and Copilot instructions.
4. Official and maintainer organizations: Vercel, FastAPI, .NET, Kotlin, Laravel, Cloudflare, AWS, Firebase, Redis, Neon, Auth0, Clerk, Better Auth, Stripe, Trigger.dev, Render, VTEX, Spree, Litestar, Salvo, and others.
5. Framework depth across Node.js/Fastify, Python/FastAPI/Django/Litestar/Flask, Java/Spring Boot, Kotlin, Go, Rust/Salvo, PHP/Laravel/Symfony, Ruby/Rails/Spree, ASP.NET Core, NestJS, and Elysia/Bun.
6. Long-tail searches for idempotency, signed webhooks, retries, DLQs, backpressure, cache invalidation/stampedes, graceful shutdown, structured logging, request context, realtime, file uploads, rate limiting, payment workflows, and concurrency conflicts.
7. Eight multilingual GitHub/web query variants in Russian, Chinese, Japanese, Korean, Spanish, Portuguese, Arabic, and German. Results mostly converged on the same English-language upstream repositories or generic packs.
8. Four social/community discovery searches across Reddit, Hacker News, YouTube, and X-indexed results. Social results were used only as discovery leads, never as canonical evidence.
9. Gap-driven second pass for AWS serverless, Kafka, Spring resilience, .NET diagnostics, Rails jobs/auth/API versioning, Rust lifecycle/realtime, and transactional-outbox candidates.
10. Saturation pass: later broad searches increasingly returned adapter copies, generic personas, documentation, provider matrices not individually reviewed, or mass-generated packs with weaker provenance.

## Source snapshots

- `https://github.com/auth0/agent-skills` @ `7af37fe227ec`
- `https://github.com/aws/agent-toolkit-for-aws` @ `21be51827dee`
- `https://github.com/better-auth/skills` @ `17dfe3a1da1c`
- `https://github.com/clerk/skills` @ `aac39ed99f18`
- `https://github.com/cloudflare/skills` @ `f96bff754e42`
- `https://github.com/dash0hq/agent-skills` @ `269e4836f459`
- `https://github.com/dodopayments/skills` @ `d582cfb3d347`
- `https://github.com/dotnet/skills` @ `a3cb4a2a9f3e`
- `https://github.com/elysiajs/skills` @ `8fd8031b83bc`
- `https://github.com/fastapi/fastapi` @ `49033471594e`
- `https://github.com/firebase/agent-skills` @ `a0b4e143f40c`
- `https://github.com/github/awesome-copilot` @ `634b92f88748`
- `https://github.com/giuseppe-trisciuoglio/developer-kit` @ `50f0b945bd81`
- `https://github.com/hookdeck/webhook-skills` @ `7e3cdbceb78d`
- `https://github.com/igmarin/rails-agent-skills` @ `2b21cddd2646`
- `https://github.com/Kotlin/kotlin-agent-skills` @ `08d7ad0d74a9`
- `https://github.com/laravel/boost` @ `613d0ebbe072`
- `https://github.com/lensesio/agentic-engineering-for-apache-kafka` @ `8cee08b1681c`
- `https://github.com/litestar-org/litestar-skills` @ `84587b4ccb97`
- `https://github.com/mcollina/skills` @ `856efd268ae8`
- `https://github.com/neondatabase/agent-skills` @ `46498bcde91c`
- `https://github.com/prisma/skills` @ `808913c1dac1`
- `https://github.com/redis/agent-skills` @ `172fb9effa13`
- `https://github.com/render-oss/skills` @ `3f2aa30eaadc`
- `https://github.com/salvo-rs/salvo-skills` @ `4dd929857cf4`
- `https://github.com/samber/cc-skills-golang` @ `147c0679e244`
- `https://github.com/spree/agent-skills` @ `a52feb91dbbc`
- `https://github.com/stripe/ai` @ `1dc126b93cc6`
- `https://github.com/triggerdotdev/skills` @ `e0f9f87153d1`
- `https://github.com/triggerdotdev/staff-engineering-skills` @ `597da099e4b7`
- `https://github.com/vercel/vercel-plugin` @ `c4a1c4e2e16f`
- `https://github.com/vintasoftware/django-ai-plugins` @ `b8af2688d994`
- `https://github.com/vtex/skills` @ `2a2a31da155d`

## Deduplication decisions

Canonical source trees were retained once. Stripe Claude/Cursor/Codex/Grok/plugin copies, VTEX OpenCode and track exports, Redis/Neon/Litestar/Vinta plugin copies, and AWS plugin copies were counted as duplicate candidates, not separate skills. Node.js, Fastify, Litestar, Auth0, AWS serverless, and Salvo realtime umbrella files were not imported alongside their granular procedures. A lower-provenance NestJS best-practices candidate was rejected in favor of GitHub's detailed NestJS instruction.

## Canonical and license decisions

Exact blob paths are stored in every accepted source_url and source_detail. Licenses were recorded only when a repository license was observed: MIT and Apache-2.0 are mirror-allowed; repositories without an observed license remain `license=unknown` and `mirror_allowed=false`. Verification status reflects opened content and canonical path inspection, not license availability.

## Limitations

Public web/GitHub/skills.sh discovery cannot prove global exhaustiveness. Social indexing is incomplete, especially X, Instagram, TikTok, private Discord/Slack communities, and unindexed video transcripts/comments. The AWS checkout hit Windows path-length limits, so exact selected files were read from the cloned Git object database with `git show`; their blob paths and repository revision were still verified. No ordinary documentation page was imported as a published skill. Derived workflow ideas remain separate.

Accepted 259 verified entries after dedupe; corrected 23 existing records; documented 191 duplicate candidates and 26 rejected/deferred candidates.

## Validation and manual duplicate audit

- `scripts/validate.py`: 658 skills, 25 categories, 658 unique slugs.
- `scripts/deduplicate.py`: 0 candidates after the two Auth0 framework-specific titles were made unambiguous; their source files remain distinct FastAPI and Fastify procedures.
- Manual same-repository name-similarity review at a lower 0.72 threshold inspected 164 pairs. High-similarity families were materially distinct framework/provider procedures (for example Auth0 framework integrations, Hookdeck provider signature schemes, Spring Java/Kotlin variants, and Azure Functions versus Durable Functions); no unintended duplicate remained.
- Exact locator audit: all 259 new records have a direct GitHub blob URL ending in their stored `source_detail`; 0 failures, 0 repeated locators, and 0 normalized-name collisions.
- License/mirroring audit: 0 mismatches between observed MIT/Apache-2.0 repositories and `mirror_allowed`; all NOASSERTION repositories remain `license=unknown` and non-mirrorable.
- Generator replay produced the same tracked diff hash on the second run.
