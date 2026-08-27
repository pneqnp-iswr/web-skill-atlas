# Contributing

Contributions should make the atlas more accurate, more useful, or easier to maintain. Small corrections are welcome.

## Add a skill

A qualifying entry is a reusable instruction set, rule, workflow, or agent procedure for a concrete web-development task. A library, framework, product, or documentation homepage is not a skill by itself.

For a new entry, provide:

- `name` — the published or natural skill name;
- `description` — one concise sentence describing the repeatable task;
- `source_url` — the original repository file, published skill, or official documentation when possible;
- `category` and `subcategory` — using the existing taxonomy where it fits;
- source detail sufficient to distinguish the entry from mirrors, forks, and nearby skills.

Use the [Suggest a skill](https://github.com/pneqnp-iswr/web-skill-atlas/issues/new/choose) issue form if you do not want to edit the dataset directly.

## Source and provenance rules

Prefer the canonical source over a registry mirror, awesome list, social post, or copied repository. Discovery sources may point to a candidate, but they do not make an entry `verified` on their own.

Do not:

- create multiple entries for forks or registry copies of the same skill;
- invent granular variants that the upstream source does not publish;
- guess a license, author, or verification status;
- paste third-party skill text unless redistribution is permitted and attribution requirements are met.

If provenance is incomplete, use the existing status model rather than overstating confidence. See [`docs/methodology.md`](docs/methodology.md).

## Fix an existing entry

Issues and pull requests are also welcome for:

- broken or redirected sources;
- duplicates and mirrors;
- incorrect metadata;
- category or taxonomy problems;
- license or attribution concerns;
- deprecated or unavailable upstreams.

The [data problem](https://github.com/pneqnp-iswr/web-skill-atlas/issues/new/choose) issue form is the fastest route for a correction that does not need a code change.

## Generated files

`data/skills.json` is the canonical skill dataset. Several files are generated from it, including category pages, compact indexes, statistics, and generated README blocks.

Do not hand-edit generated counts or category tables. Update the source data or presentation template, then run the generator.

## Local checks

Run these before opening a pull request:

```bash
python scripts/validate.py
python scripts/deduplicate.py
python scripts/generate.py
git diff --exit-code
```

A clean final `git diff` confirms that generated files are committed and the generator is deterministic for the current dataset.

## Pull requests

Keep a pull request focused. Explain what changed, link the relevant canonical source, and include evidence for provenance or metadata corrections when needed.
