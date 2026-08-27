# Coverage gaps

Priority is categories with low verified coverage and ecosystems represented mainly through discovery indexes.

- E-commerce: 0 entries
- Git / GitHub: 1 entry
- Analytics: 2 entries
- Internationalization: 2 entries
- PWA: 2 entries
- Content: 4 entries
- AI Web Development: 5 entries
- Accessibility: 5 entries
- Code Quality: 5 entries
- Interaction: 5 entries
- SEO: 5 entries
- Deployment: 6 entries
- DevOps: 6 entries
- Components: 7 entries
- Product: 8 entries
- Debugging: 9 entries

## Design long-tail

Design now has broad coverage across UI/UX, product design, design systems, responsive design, typography, motion, accessibility, Figma workflows, landing pages, dashboards, visual QA, and anti-generic-interface review.

The weakest design areas are standalone procedures for narrow component and state problems: advanced data-table UX, checkout flow audits, form micro-UX, navigation variants, border/radius/elevation consistency, empty/loading/error states, and highly specific spacing or density audits. These should be targeted in later gap-driven passes instead of inventing entries from general design guidance.

Next non-design passes should target e-commerce, Git/GitHub workflows, i18n/RTL, PWA, deployment, and the backend long-tail gaps recorded below.

## 2026-08-27 Frontend deep research pass

Frontend coverage improved substantially in state management, routing, URL state, data fetching, forms, rendering, error handling, virtualization, accessibility, and performance. Remaining highest-value gaps are CSS engineering, DOM/browser APIs, storage/workers, Web Components, Safari/mobile quirks, real-time UI, browser debugging/memory profiling, chunk-load recovery, and long-tail framework coverage (Solid/Qwik/Preact/Lit/Alpine/HTMX). See `research/frontend-2026-08-27/frontend-gaps.md`.

## 2026-08-27 Backend deep research pass

Backend coverage now spans major server frameworks plus idempotency, retries, DLQs, backpressure, caching, graceful shutdown, structured logging, authentication, realtime, files, payments, and serverless workflows. The largest remaining gaps are general transactional outbox, RabbitMQ retry/DLX, cursor pagination, optimistic locking, distributed-lock fencing, request deadline propagation, provider-neutral circuit breakers, request-ID propagation, and broader official Flask/Django/Go/Rust/Spring application-skill provenance. See `research/backend-2026-08-27/backend-gaps.md`.
