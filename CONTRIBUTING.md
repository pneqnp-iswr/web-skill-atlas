# Contributing

Pull requests may add a skill/source, correct metadata, change classification, add a category, repair a broken URL, mark a deprecated entry, or improve the taxonomy.

Minimum new-entry metadata: name, concise description, source URL, primary category, and source detail when multiple skills share one repository. Prefer the original source. Check for duplicates before submitting. Do not paste third-party skill text unless its license explicitly permits redistribution and attribution is preserved.

Before opening a PR:

```sh
python scripts/validate.py
python scripts/deduplicate.py
python scripts/generate.py
git diff --exit-code
```
