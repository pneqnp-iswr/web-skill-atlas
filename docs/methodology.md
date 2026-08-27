# Methodology

The catalog follows a discovery → upstream verification → normalization → deduplication → scoring pipeline.

1. Search registries, GitHub collections, official repositories, documentation, developer communities, and publicly indexed social/video surfaces.
2. Treat social posts and curated lists as discovery leads, not proof. Prefer the original repository or official documentation as the canonical source.
3. Reject ordinary libraries unless the source exposes a reusable skill/rule/workflow.
4. Keep independently published granular rule files granular; do not manufacture variants merely to increase counts.
5. Record incomplete provenance as `partially-verified`.
6. Mark documentation-derived procedures as `derived-workflow`, never as third-party published skills.
7. Re-run validation and generated-data checks on every pull request.
