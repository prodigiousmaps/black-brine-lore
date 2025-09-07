# Black Brine — Refactor & Normalize (One-Click Guide)

## What this does
- Scans `RPG_Knowledge_Base/` for Markdown files with YAML front-matter.
- Ensures every file has `type`, `id`, `name`.
- Normalizes relationship fields to canonical ids using `aliases/aliases.yaml` (plus fuzzy matching).
- Builds patches (safe, non-destructive) in `/patches`.
- Generates a review dashboard at `docs/refactor_report.html`.
- (Optional) Applies patches in-place when you add `--apply`.

## Install dependencies (Windows)
```
py -3.13 -m pip install pyyaml rapidfuzz
```

*(Optional)* If you want better name extraction later, we can add spaCy.

## Files in this pack
- `bb_schema.yaml` — human-readable standard you can tweak.
- `bb_refactor.py` — the refactor/normalize script.
- Report outputs:
  - `docs/refactor_suggestions.json`
  - `docs/refactor_report.html`
- Patches to apply (if desired):
  - `patches/*.yml`

## How to run
1. Put `bb_refactor.py` at the **repo root** (same level as `RPG_Knowledge_Base/`).
2. Make sure you have `aliases/aliases.yaml` with at least a few key names → ids.
3. Run a dry run:
```
py -3.13 bb_refactor.py
```
4. Open the report in your browser:
   - If you use GitHub Pages: `https://<you>.github.io/black-brine-lore/refactor_report.html`
   - Or open `docs/refactor_report.html` locally.
5. If it looks good, apply patches:
```
py -3.13 bb_refactor.py --apply
```
6. Rebuild the graph and push:
```
py -3.13 indexer.py
git add -A && git commit -m "normalize yaml via refactor" && git push
```

## Campaign notes → narrative
- Set `type: story` (or `event`) in front-matter.
- If `summary` is missing, the refactor will auto-create a short summary from the first paragraph of the body.
- Add `location:` and `participants:` (names or ids). The enrichment/indexer will wire edges.

## Tips
- Add every variant name you use once to `aliases/aliases.yaml`. Everything else will resolve automatically.
- You can safely re-run the refactor anytime; it only changes fields when it improves them.
