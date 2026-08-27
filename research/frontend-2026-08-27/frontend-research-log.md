# Frontend research log — 2026-08-27

## Scope and counting

This pass was frontend engineering only. The candidate-review figure is a conservative count of concrete skill files, rule files, repository-level candidate packs, and existing atlas entries that were explicitly triaged; raw search-result counts were not treated as reviewed candidates. A 600-variant query matrix was generated across frameworks, task families, file conventions, repositories, code search, skills registries, and long-tail failure modes.

## Waves executed

1. Existing atlas baseline and adjacent-category deduplication.
2. Official and maintainer skills repositories.
3. skills.sh and curated-registry discovery followed by upstream tracing.
4. GitHub repository and code search for SKILL.md, rules, instructions, AGENTS.md, Cursor/Copilot-style procedures.
5. Framework organizations: React Router, Svelte, Vue, Angular, Astro, Qwik, TanStack and related maintainers.
6. State/data/forms/routing deep search: Redux Toolkit, TanStack Router/Query, next-safe-action, Effector.
7. Long-tail frontend tasks: hydration, URL state, code splitting, error boundaries, virtualization, cache invalidation, optimistic state.
8. Accessibility/performance reusable-instruction search.
9. Multilingual discovery queries in Russian, Chinese, Japanese, Spanish, Portuguese, and Korean. These mostly converged on the same English-language GitHub corpora and mirrors rather than a separate regional skill ecosystem.
10. Gap-driven and saturation pass. Broad searches increasingly returned generic frontend personas, design skills, browser-operation tools, framework-maintainer procedures, mirrors, or mass packs with weak provenance.

## Strong canonical sources

- reduxjs/redux-toolkit: eight task-oriented official skills, MIT, with source lists and explicit wrong/correct patterns.
- sveltejs/ai-tools: official Svelte skill distributed through multiple agent adapters; one canonical source retained.
- vuejs-ai/skills: canonical upstream for Vue best-practice/debug/testing skill families and granular references.
- TanStack/router: official router-core skill tree with nine independent sub-skills and a core router skill.
- github/awesome-copilot: reusable accessibility and performance instructions with detection/severity/fixes.
- next-safe-action/skills: maintainer-published form and TanStack Query integration procedures.
- demark-pro/skills: focused Effector and Feature-Sliced Design frontend procedures.

## Deduplication decisions

React Router and TanStack Router existing atlas records were corrected to current official upstreams rather than duplicated. Vue Debug Guides and Vue Testing Best Practices were moved from an older mirror namespace to vuejs-ai/skills. Svelte adapter copies for Claude, Cursor, and OpenCode were treated as mirrors of one canonical skill. Generic broad frontend personas were rejected when they overlapped more precise, higher-provenance procedures.

## Verification rule

Every newly accepted published entry points to an opened public file whose contents match the claimed capability. Licenses were recorded only when a repository/file license was observed; DeckardGer/tanstack-agent-skills and next-safe-action/skills remain license=unknown because no repository LICENSE file was verified during this pass.

