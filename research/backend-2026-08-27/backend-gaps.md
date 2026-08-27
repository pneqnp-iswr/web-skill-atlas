# Backend coverage gaps

The pass materially improves framework and production-hardening coverage, but the following gaps remain real and should not be filled by converting ordinary documentation into fake published skills.

## Highest-priority gaps

- **Transactional outbox:** one strong Sentry-internal skill was found, but it is coupled to Sentry's data model and deployment mechanics. No general reusable published skill passed the provenance and uniqueness bar.
- **RabbitMQ:** official documentation exists for acknowledgements, publisher confirms, retries, quorum queues, and dead-letter exchanges, but no strong public agent skill was verified.
- **Cursor pagination:** GraphQL and framework references touch pagination, but a focused cross-stack cursor contract and stable-ordering workflow remains absent.
- **Optimistic locking:** concurrency and transaction skills cover adjacent mechanisms; a focused version-column/conflict-recovery skill is still missing.
- **Distributed locking with fencing:** Redis locking guidance exists, but the critical fencing-token workflow is not represented by a verified published skill.
- **Deadline propagation:** Go context and framework timeout skills exist; a cross-service remaining-budget propagation audit is not.
- **Request ID propagation:** logging and OpenTelemetry coverage is strong, but a focused ingress-to-queue-to-downstream correlation workflow remains missing.
- **Provider-neutral circuit breakers:** Spring Resilience4j and AWS material are present; a language-neutral implementation/review skill is not.
- **Large streaming uploads:** ASP.NET and Salvo skills cover files, but a cross-stack abort-safe stream-to-object-storage procedure remains sparse.
- **Session rotation/reuse detection:** Auth0 and Better Auth provide provider-specific guidance; a provider-neutral session-token lifecycle audit is absent.

## Framework provenance gaps

- Official Flask and Django repositories did not expose consumer-facing application skills; accepted Python coverage comes from FastAPI/Litestar official trees and Vinta/Auth0 maintainers.
- Official Spring Boot sources did not expose an application SKILL.md; GitHub Copilot instructions and a reviewed MIT Spring skill pack provide coverage.
- Official Go and Rust language repositories did not expose application-development skills; Go coverage comes from a maintainer pack and Rust web coverage from Salvo's official organization.
- Express is covered most strongly through Auth0 framework procedures; a current official Express application skill was not verified.
- RabbitMQ, Phoenix/Elixir, Ktor, Actix/Axum, Flask core application patterns, and generic PHP backend workflows remain thinner than Node.js, Go, Rust/Salvo, Spring, .NET, and Rails/Spree.

## Research limitations

Multilingual searches mostly returned the same English-language upstreams or mirrors. Social discovery was limited to publicly indexed results and cannot cover private communities, exhaustive X/Instagram/TikTok content, or all video comments/transcripts. Provider-specific mega-repositories were sampled and only individually opened files were accepted; unreviewed tails remain deferred rather than partially verified.
