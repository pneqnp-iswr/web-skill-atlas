# Backend deep research summary

## Scope and totals

- Candidates reviewed: 499
- Query variants generated: 600 (generated matrix, not 600 executed searches)
- New accepted after dedupe: 259
- Documented duplicate candidates: 191
- Rejected or deferred: 26
- Metadata corrections: 23
- Backend count: 6 -> 98
- New verified: 259
- New partially verified: 0
- Unique canonical repositories represented by new entries: 31
- Unique new/updated source records in this pass: 34
- Unique source records newly added to data/sources.json: 30 (one obsolete Clerk source record was removed)

The pass is backend-focused but preserves atlas category boundaries: API protocols remain in APIs; auth hardening in Security; ORM/data access in Databases; distributed-system patterns in Architecture; framework tests in Testing; caching/profiling in Performance; and deployment-only procedures in Deployment.

## Quality distribution

- 85-89: 155
- 90-100: 38
- 80-84: 66

## Top 50 backend-related entries

- **FastAPI Application Engineering** - Backend / FastAPI - 94 - verified
- **AWS Lambda Durable Functions** - Architecture / Workflow Orchestration - 93 - verified
- **Distributed Systems Backpressure** - Performance / Backpressure - 92 - verified
- **Distributed Systems Idempotency** - Architecture / Idempotency - 92 - verified
- **Distributed Systems Retry Storms** - Architecture / Retries & Failure Handling - 92 - verified
- **.NET 11 System.Text.Json** - Backend / Backend Engineering - 91 - verified
- **.NET Performance Analysis** - Performance / Server Performance - 91 - verified
- **.NET Production Trace Collection** - Debugging / Production Diagnostics - 91 - verified
- **ASP.NET Core OpenTelemetry Configuration** - Backend / Observability - 91 - verified
- **ASP.NET Core Web API Engineering** - Backend / API Implementation - 91 - verified
- **AWS S3 Upload Routing with Step Functions** - Architecture / Routing & Middleware - 91 - verified
- **AWS Step Functions** - Architecture / Workflow Orchestration - 91 - verified
- **Cloudflare Agents SDK Backend** - Backend / Backend Engineering - 91 - verified
- **Cloudflare Durable Objects** - Architecture / Stateful Serverless - 91 - verified
- **Cloudflare Email Service** - Backend / Backend Engineering - 91 - verified
- **Cloudflare Turnstile Server Verification** - Security / Application Security - 91 - verified
- **Cloudflare Workers Production Best Practices** - Backend / Backend Engineering - 91 - verified
- **Data-Driven ASP.NET Core Scaffolding** - Backend / Backend Engineering - 91 - verified
- **Minimal API File Upload** - Backend / File & Object Handling - 91 - verified
- **Node.js Graceful Shutdown** - Backend / Graceful Shutdown - 91 - verified
- **Optimizing EF Core Queries** - Performance / Data Access - 91 - verified
- **Stripe API and SDK Upgrade** - Backend / API Implementation - 91 - verified
- **Stripe Apps** - Backend / Backend Engineering - 91 - verified
- **Stripe Connect KYC Requirements** - Security / Identity Verification - 91 - verified
- **Distributed Systems Cache Invalidation** - Performance / Caching - 90 - verified
- **Distributed Systems Cardinality** - Performance / Distributed Systems - 90 - verified
- **Distributed Systems Clock Skew** - Architecture / Distributed Systems - 90 - verified
- **Distributed Systems Consistency Models** - Architecture / Distributed Systems - 90 - verified
- **Distributed Systems Denormalization** - Architecture / Distributed Systems - 90 - verified
- **Distributed Systems Fallacies** - Architecture / Distributed Systems - 90 - verified
- **Distributed Systems Hot Partitions** - Architecture / Partitioning & Sharding - 90 - verified
- **Distributed Systems Memory Leaks** - Performance / Distributed Systems - 90 - verified
- **Distributed Systems Race Conditions** - Architecture / Concurrency - 90 - verified
- **Distributed Systems Sharding** - Architecture / Partitioning & Sharding - 90 - verified
- **Distributed Systems Streams Vs Batch** - Architecture / Distributed Systems - 90 - verified
- **Distributed Systems Thundering Herd** - Performance / Caching - 90 - verified
- **Idempotent Webhook Handler Patterns** - APIs / Webhooks - 90 - verified
- **Object Storage as a Database** - Databases / File & Object Handling - 90 - verified
- **Amazon SES** - Backend / Streaming - 89 - verified
- **Auth0 Application Security Review** - Security / Application Security - 89 - verified
- **Auth0 ASP.NET Core API Authorization** - Security / Authorization - 89 - verified
- **Auth0 Authentication Rate Limiting** - Security / Authentication - 89 - verified
- **Auth0 Express JWT API Authorization** - Security / Authentication - 89 - verified
- **Auth0 Express Web Application Authentication** - Security / Authentication - 89 - verified
- **Auth0 Flask Authentication** - Security / Authentication - 89 - verified
- **Auth0 Go API Authorization** - Security / Authorization - 89 - verified
- **Auth0 Java MVC Authentication** - Security / Authentication - 89 - verified
- **Auth0 Laravel API Authorization** - Security / Authorization - 89 - verified
- **Auth0 PHP API Authorization** - Security / Authorization - 89 - verified
- **Auth0 Spring Boot API Authorization** - Security / Authorization - 89 - verified

## Framework and platform coverage

- Node.js: 31
- Salvo: 27
- Fastify: 20
- Go standard library: 20
- Spring Boot: 17
- Litestar: 15
- Ruby on Rails: 14
- ASP.NET Core: 11
- Apache Kafka: 8
- .NET: 8
- Spree: 8
- VTEX IO: 8
- AWS Lambda: 7
- Trigger.dev: 6
- Dodo Payments: 6
- Redis: 6
- Django: 5
- Django REST Framework: 5
- Cloudflare Workers: 5
- Better Auth: 5
- Auth0: 4
- Firebase: 4
- Stripe: 4
- Render: 3
- Neon: 3
- FastAPI: 2
- Laravel: 2
- Azure Functions: 2
- OpenTelemetry: 2
- Clerk: 2
- Express: 2
- Elysia: 1
- Bun: 1
- Kotlin: 1
- JPA: 1
- AWS AppSync: 1
- NestJS: 1
- Symfony: 1
- Flask: 1
- Go HTTP: 1
- Java MVC: 1
- PHP: 1

## Task-family coverage

- Backend Engineering: 59
- Authentication: 18
- Webhooks: 15
- Application Security: 12
- Backend Testing: 9
- Data Access: 9
- Server Performance: 8
- Caching: 7
- Distributed Systems: 7
- Authorization: 7
- Payments & Billing: 7
- API Implementation: 6
- Error Handling: 5
- Routing & Middleware: 5
- OpenAPI: 5
- Observability: 5
- Jobs & Queues: 5
- Workflow Orchestration: 5
- Server-Sent Events & Realtime: 4
- File & Object Handling: 4
- Dependency Injection: 4
- Logging & Correlation: 3
- Rate Limiting: 3
- Configuration: 2
- Graceful Shutdown: 2
- Streaming: 2
- WebSockets: 2
- Concurrency: 2
- GraphQL: 2
- Partitioning & Sharding: 2
- Idempotency: 2
- Retries & Failure Handling: 2
- Backend Deployment: 1
- Timeouts & Cancellation: 1
- TLS & Certificates: 1
- gRPC: 1
- Backend Refactoring: 1
- Go Safety: 1
- Backpressure: 1
- Kafka Operations: 1
- Kafka Connect: 1
- Consumer Lag: 1
- Schema Evolution: 1
- FastAPI: 1
- Elysia: 1
- Laravel: 1
- Backend Review: 1
- Safe Migrations: 1
- ORM Mapping: 1
- Production Diagnostics: 1
- Event-Driven Architecture: 1
- Resilience: 1
- API Versioning: 1
- REST APIs: 1
- Stateful Serverless: 1
- AI Backend Agents: 1
- Token Lifecycle: 1
- Asynchronous Payments: 1
- Datastore Observability: 1
- Identity Verification: 1
- API Gateway: 1

## Important source families

- mcollina/skills for granular Node.js and Fastify production rules.
- salvo-rs/salvo-skills and samber/cc-skills-golang for Rust and Go depth.
- triggerdotdev/staff-engineering-skills for concrete distributed-systems failure modes.
- fastapi/fastapi, dotnet/skills, Kotlin/kotlin-agent-skills, laravel/boost, litestar-org/litestar-skills, and spree/agent-skills for framework-owned or framework-focused procedures.
- auth0/agent-skills, clerk/skills, better-auth/skills, stripe/ai, hookdeck/webhook-skills, redis/agent-skills, firebase/agent-skills, cloudflare/skills, and aws/agent-toolkit-for-aws for provider-specific backend operations.

## Canonical corrections

- Five Vercel Backend records now point to exact SKILL.md blobs instead of directory pages.
- Six Clerk records moved from the obsolete clerk/clerk-skills root to exact files in clerk/skills.
- Six Auth0 frontend records moved to exact current references in auth0/agent-skills and gained the observed Apache-2.0 license.
- Better Auth now points to its exact best-practices file.
- Five Prisma records now point to exact current files, record MIT, and the obsolete Migrate label was corrected to the current Prisma CLI workflow.

## Highest-value long-tail coverage

Idempotent webhook handling, provider signature verification, queue/DLQ review, retry storms, thundering-herd prevention, cache invalidation, backpressure, graceful shutdown, request context cancellation, safe Django migrations, Kafka consumer lag, auth token rotation, WebSocket/SSE lifecycle, file uploads, payment idempotency, and serverless timeout diagnosis are all represented by concrete accepted source files.

## Gaps and limitations

The largest remaining gaps are a general transactional-outbox skill, RabbitMQ-specific retry/DLX implementation, provider-neutral cursor pagination, optimistic-lock conflict recovery, distributed-lock fencing, deadline-budget propagation, and a general request-ID propagation audit. Official Flask, Django, Go, Rust, and Spring repositories did not expose consumer-facing application SKILL.md files in the inspected trees, so maintainer/community sources are clearly identified. Social and multilingual search were discovery-only and cannot be claimed exhaustive; X/Instagram/TikTok indexing and closed community content remain incomplete.

## Local validation

- Schema/taxonomy validation: 658 skills, 25 categories, 658 unique slugs.
- Duplicate detector: 0 candidates; a lower-threshold manual same-repository audit found only intentional framework/provider variants.
- Exact source locator audit: 259/259 direct blob URLs matched their `source_detail`.
- Issue-form validation and secret scan passed.
- Generator second-run determinism passed.
