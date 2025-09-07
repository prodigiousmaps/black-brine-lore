#!/usr/bin/env python3
"""
bb_refactor.py — Refactor & Normalize Black Brine YAML

What it does (non-destructive by default):
- Walks RPG_Knowledge_Base/, parses Markdown with YAML front-matter.
- Ensures minimal schema fields exist; generates ids if missing.
- Normalizes relationship fields to canonical ids using aliases/aliases.yaml.
- Infers type from folder name when missing.
- Suggests/normalizes allies/rivals/enemies/appears_in/leaders/controls/participants (high confidence only).
- Emits patches/*.yml and a docs/refactor_report.html for review.
- With --apply, patches are written back to source files in-place.

Usage:
  py -3.13 bb_refactor.py            # dry run (suggestions + patches + report)
  py -3.13 bb_refactor.py --apply    # apply patches after reviewing

Prereqs:
  py -3.13 -m pip install pyyaml rapidfuzz
"""

from __future__ import annotations
import json
import pathlib
import re
import sys
from collections import defaultdict
from typing import Tuple, List, Dict, Any

import yaml  # PyYAML

# Optional fuzzy resolver (falls back to exact/alias-only if unavailable)
try:
    from rapidfuzz import process, fuzz
    HAVE_FUZZ = True
except Exception:
    HAVE_FUZZ = False

# ---------- Paths ----------
ROOT = pathlib.Path(__file__).parent.resolve()
SRC = ROOT / "RPG_Knowledge_Base"
PATCH_DIR = ROOT / "patches"
DOCS_DIR = ROOT / "docs"
ALIAS_FILE = ROOT / "aliases" / "aliases.yaml"

PATCH_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Parsing ----------
FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

def read_fm_body(p: pathlib.Path) -> Tuple[Dict[str, Any], str]:
    """Return (front_matter_dict, body_text). Safe for malformed YAML."""
    text = p.read_text(encoding="utf-8", errors="ignore")
    m = FM_RE.match(text)
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
            if not isinstance(fm, dict):
                fm = {}
        except Exception:
            fm = {}
        body = text[m.end():]
    else:
        try:
            fm = yaml.safe_load(text) or {}
            if not isinstance(fm, dict):
                fm = {}
        except Exception:
            fm = {}
        body = ""
    return fm, body

def write_fm_body(p: pathlib.Path, fm: Dict[str, Any], body: str) -> None:
    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True)
    p.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")

def slugify(s: str) -> str:
    return re.sub(r'[^a-z0-9\-]+', '-', s.lower().replace(' ', '-')).strip('-')

def as_list(x: Any) -> List[Any]:
    if x is None:
        return []
    return x if isinstance(x, list) else [x]

# ---------- Type inference from folders (best-effort) ----------
TYPE_GUESS_MAP = {
    "npc": "npc", "npcs": "npc", "characters": "npc",
    "faction": "faction", "factions": "faction",
    "organizations": "organization", "organization": "organization",
    "city": "city", "district": "district", "districts": "district",
    "locations": "location", "location": "location", "poi": "location", "places": "location",
    "items": "item", "item": "item",
    "stories": "story", "story": "story", "events": "event", "event": "event",
    "campaign": "story", "notes": "story",
}

def guess_type_from_path(p: pathlib.Path) -> str | None:
    for part in reversed(p.parts):
        key = part.lower()
        # strip numeric prefixes like 10_ or 11_
        key = re.sub(r'^\d+_', '', key)
        if key in TYPE_GUESS_MAP:
            return TYPE_GUESS_MAP[key]
    return None

# ---------- Load aliases (name -> id) ----------
aliases: Dict[str, str] = {}
if ALIAS_FILE.exists():
    try:
        ad = yaml.safe_load(ALIAS_FILE.read_text(encoding="utf-8")) or {}
        aliases = ad.get("aliases", {}) or {}
    except Exception:
        aliases = {}

# ---------- Scan files, collect nodes & gazetteer ----------
Node = Dict[str, Any]
nodes: List[Node] = []
name_to_id: Dict[str, str] = {}
id_to_name: Dict[str, str] = {}

if not SRC.exists():
    print(f"[refactor] WARN: {SRC} does not exist.")
else:
    for p in SRC.rglob("*.md"):
        # Skip template area and *.ignore files
        if "08_Templates" in p.parts or p.name.endswith(".ignore"):
            continue
        fm, body = read_fm_body(p)
        ntype = fm.get("type") or guess_type_from_path(p) or "page"
        name = fm.get("name") or p.stem.replace("_", " ").strip()
        nid = fm.get("id") or f"bb:{ntype}:{slugify(p.stem)}"

        # Ensure basics exist in memory (patch emitted later)
        fm.setdefault("type", ntype)
        fm.setdefault("name", name)
        fm.setdefault("id", nid)

        node = {
            "id": nid,
            "name": name,
            "type": ntype,
            "path": str(p.relative_to(ROOT)),
            "fm": fm,
            "body": body,
        }
        nodes.append(node)
        id_to_name[nid] = name
        name_to_id[name.lower()] = nid
        for aka in as_list(fm.get("aliases")):
            if isinstance(aka, str):
                name_to_id[aka.lower()] = nid

# Fold in aliases.yaml (name -> id)
for k, v in aliases.items():
    if isinstance(k, str) and isinstance(v, str):
        name_to_id[k.lower()] = v

# ---------- Resolver ----------
def resolve_ref(val: Any) -> Tuple[str | None, str, float]:
    """Resolve a string reference to a canonical id.
    Returns (id_or_None, method: 'id'|'alias'|'fuzzy'|'none', score[0..1]).
    """
    if not isinstance(val, str):
        return (None, "none", 0.0)
    v = val.strip()
    if not v:
        return (None, "none", 0.0)
    # direct canonical id
    if v in id_to_name:
        return (v, "id", 1.0)
    # alias by name
    hit = name_to_id.get(v.lower())
    if hit:
        return (hit, "alias", 1.0)
    # fuzzy (optional)
    if HAVE_FUZZ and name_to_id:
        choices = list(name_to_id.keys())
        match = process.extractOne(v.lower(), choices, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= 90:
            return (name_to_id[match[0]], "fuzzy", match[1] / 100.0)
    return (None, "none", 0.0)

# ---------- Suggestions & patches ----------
suggestions: List[Dict[str, Any]] = []
patch_manifest: List[str] = []
by_file: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"set": {}, "path": ""})

def add_suggestion(path: str, field: str, value: Any, rid: str | None, method: str, score: float, note: str = ""):
    suggestions.append({
        "path": path,
        "field": field,
        "value": value,
        "resolved_id": rid,
        "method": method,
        "score": round(float(score), 3),
        "note": note,
    })

AUTO_THRESH = 0.92  # normalize to ids when id/alias or fuzzy >= 0.92

for n in nodes:
    path = n["path"]
    fm = n["fm"]
    body = n["body"]
    by_file[path]["path"] = path

    # Ensure required basics (type/id/name)
    for req in ("type", "id", "name"):
        if req not in fm or not fm[req]:
            if req == "type":
                fm["type"] = guess_type_from_path(pathlib.Path(path)) or "page"
            elif req == "id":
                fm["id"] = f"bb:{fm.get('type','page')}:{slugify(pathlib.Path(path).stem)}"
            elif req == "name":
                fm["name"] = pathlib.Path(path).stem.replace("_", " ")
            by_file[path]["set"][req] = fm[req]

    # Normalize location-like fields to IDs
    for fld in ("location", "parent_location", "city"):
        vals = as_list(fm.get(fld))
        if not vals:
            continue
        out, touched = [], False
        for v in vals:
            if not isinstance(v, str):
                out.append(v)
                continue
            rid, method, score = resolve_ref(v)
            add_suggestion(path, fld, v, rid, method, score)
            if rid:
                out.append(rid)
                if method != "id":
                    touched = True
            else:
                out.append(v)
        if out and touched:
            by_file[path]["set"][fld] = out[0] if len(out) == 1 else out

    # factions → ids (collapse to 'factions' list)
    fvals = as_list(fm.get("faction")) + as_list(fm.get("factions"))
    if fvals:
        out, touched = [], False
        for v in fvals:
            if not isinstance(v, str):
                out.append(v)
                continue
            rid, method, score = resolve_ref(v)
            add_suggestion(path, "factions*", v, rid, method, score)
            if rid:
                out.append(rid)
                if method != "id":
                    touched = True
            else:
                out.append(v)
        if out and touched:
            by_file[path]["set"]["factions"] = sorted(set(out))

    # allies/rivals/enemies/appears_in/leaders/controls/participants
    for fld in ("allies", "rivals", "enemies", "appears_in", "leaders", "controls", "participants"):
        vals = as_list(fm.get(fld))
        if not vals:
            continue
        out, changed_local = [], False
        for v in vals:
            if not isinstance(v, str):
                out.append(v)
                continue
            rid, method, score = resolve_ref(v)
            add_suggestion(path, fld, v, rid, method, score)
            # normalize only when strong confidence OR already id/alias
            if rid and (method in {"id", "alias"} or score >= AUTO_THRESH):
                out.append(rid)
                changed_local = True
            else:
                out.append(v)
        if changed_local:
            by_file[path]["set"][fld] = sorted(set(out))

    # Campaign notes → narrative summary bootstrap
    if fm.get("type") in {"story", "event"} and not fm.get("summary"):
        first_para = (body.strip().split("\n\n")[0] if body.strip() else "").strip()
        if first_para:
            # compress whitespace, keep it short
            s = re.sub(r"\s+", " ", first_para)
            if len(s) > 240:
                s = s[:240] + "…"
            by_file[path]["set"]["summary"] = s

# Write patch files
def yaml_dump(obj: Any) -> str:
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)

for path, obj in by_file.items():
    if not obj["set"]:
        continue
    patch_path = PATCH_DIR / (slugify(pathlib.Path(path).stem) + ".yml")
    payload = {"path": str(ROOT / path), "set": obj["set"]}
    patch_path.write_text(yaml_dump(payload), encoding="utf-8")
    patch_manifest.append(str(patch_path.relative_to(ROOT)))

# ---------- Reports ----------
files_count = len(nodes)
patches_count = len(patch_manifest)

# suggestions JSON
suggestions_json = {
    "total_files": files_count,
    "patches": patch_manifest,
    "suggestions": suggestions[:5000],  # safety cap
}
(DOCS_DIR / "refactor_suggestions.json").write_text(
    json.dumps(suggestions_json, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

# HTML report (avoid problematic f-strings + backslashes)
html = """
<!doctype html><meta charset="utf-8"><title>Refactor Report</title>
<style>
body{font:14px/1.6 system-ui,sans-serif;background:#0a0a0b;color:#e8e8ea;margin:18px}
h1{font-size:22px;margin:0 0 8px}
table{width:100%;border-collapse:collapse;margin-top:10px}
td,th{border-bottom:1px solid #2a2d36;padding:6px 8px;text-align:left;font-size:13px}
.small{opacity:.8}
code{background:#111215;padding:1px 4px;border-radius:4px}
</style>
<h1>Black Brine Refactor Suggestions</h1>
<div class="small">Files: {FILES} • Patches: {PATCHES} (see /patches)</div>
<table>
  <thead>
    <tr><th>File</th><th>Field</th><th>Value</th><th>Resolved</th><th>Method</th><th>Score</th></tr>
  </thead>
  <tbody id="tb"></tbody>
</table>
<script>
fetch('refactor_suggestions.json').then(r => r.json()).then(d => {
  const tb = document.getElementById('tb');
  d.suggestions.forEach(s => {
    const tr = document.createElement('tr');
    const file = s.path.replace(/^.*RPG_Knowledge_Base\\//,'');
    const val  = String(s.value || '').replace(/</g,'&lt;');
    const rid  = s.resolved_id || '—';
    const score = (s.score || 0).toFixed(2);
    tr.innerHTML =
      '<td>'+file+'</td>' +
      '<td>'+s.field+'</td>' +
      '<td><code>'+val+'</code></td>' +
      '<td>'+rid+'</td>' +
      '<td>'+s.method+'</td>' +
      '<td>'+score+'</td>';
    tb.appendChild(tr);
  });
});
</script>
"""
html = html.replace("{FILES}", str(files_count)).replace("{PATCHES}", str(patches_count))
(DOCS_DIR / "refactor_report.html").write_text(html, encoding="utf-8")

print(f"[refactor] Files scanned: {files_count}")
print(f"[refactor] Patch files:   {patches_count} → {PATCH_DIR}")
print(f"[refactor] Report:        {DOCS_DIR / 'refactor_report.html'}")
print("[refactor] Dry run complete. Use --apply to write patches into sources.")

# ---------- Apply patches (optional) ----------
if "--apply" in sys.argv:
    applied = 0
    for patch_file in PATCH_DIR.glob("*.yml"):
        patch = yaml.safe_load(patch_file.read_text(encoding="utf-8")) or {}
        path = patch.get("path")
        sets = patch.get("set") or {}
        if not path or not sets:
            continue
        src = pathlib.Path(path)
        if not src.exists():
            # try relative to repo root
            src = ROOT / path
            if not src.exists():
                print(f"[refactor] missing {path}")
                continue
        fm, body = read_fm_body(src)
        changed = False
        for k, v in sets.items():
            if fm.get(k) != v:
                fm[k] = v
                changed = True
        if changed:
            write_fm_body(src, fm, body)
            applied += 1
            print(f"[refactor] applied → {src}")
    print(f"[refactor] Done. Applied {applied} patch files.")
