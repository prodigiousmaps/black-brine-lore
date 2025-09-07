#!/usr/bin/env python3
"""
indexer.py — Build docs/graph.json from YAML/Markdown lore.

Features:
- Parses YAML front-matter (and falls back to whole-file YAML if no front-matter).
- Embeds each node's full front matter as `fm` and a short `body_excerpt`.
- Resolves names via aliases/aliases.yaml and in-file aliases.
- Emits edges:
  - located_in      ← parent_location, location, city
  - member_of       ← faction, factions
  - ally_of/rival_of/enemy_of
  - appears_in      ← (story/event).participants → npc/faction/item/etc
  - appears_in      ← any_node.appears_in (direct)
  - leads           ← (faction/org).leaders → npc
  - controls        ← (faction/org).controls → location/poi
- Skips locked/unreadable files instead of crashing.
- Skips 08_Templates and *.ignore files.
- Outputs docs/graph.json
"""

import json
import pathlib
import re
import sys
import yaml

ROOT = pathlib.Path(__file__).parent
CONTENT_DIRS = ["RPG_Knowledge_Base"]
ALIAS_FILE = ROOT / "aliases" / "aliases.yaml"
OUT_DIR = ROOT / "docs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FRONTMATTER = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

# ------------------------
# Helpers
# ------------------------
def safe_read_text(p: pathlib.Path) -> str | None:
    """Read file text safely; return None if unreadable/locked."""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"[indexer] WARN: cannot read {p}: {e}", file=sys.stderr)
        return None

def parse_file_with_body(p: pathlib.Path):
    """
    Return (front_matter_dict, body_text).
    Tries YAML front-matter first; falls back to whole-file YAML; else empty fm.
    """
    text = safe_read_text(p)
    if text is None:
        return {}, ""
    m = FRONTMATTER.match(text)
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
            if not isinstance(fm, dict):
                fm = {}
        except Exception:
            fm = {}
        body = text[m.end():]
        return fm, body
    # fallback: whole-file YAML
    try:
        fm = yaml.safe_load(text) or {}
        if not isinstance(fm, dict):
            fm = {}
    except Exception:
        fm = {}
    return fm, ""

def slugify(s: str) -> str:
    return re.sub(r'[^a-z0-9\-]+', '-', s.lower().replace(' ', '-')).strip('-')

def as_list(x):
    if x is None: return []
    return x if isinstance(x, list) else [x]

# ------------------------
# Load aliases
# ------------------------
aliases_map: dict[str, str] = {}
if ALIAS_FILE.exists():
    try:
        alias_doc = yaml.safe_load(ALIAS_FILE.read_text(encoding="utf-8")) or {}
        aliases_map = alias_doc.get("aliases", {}) or {}
    except Exception as e:
        print(f"[indexer] WARN: could not parse {ALIAS_FILE}: {e}", file=sys.stderr)
        aliases_map = {}

# ------------------------
# Pass 1: collect nodes
# ------------------------
nodes: list[dict] = []
nodes_by_id: dict[str, dict] = {}
name_to_id: dict[str, str] = {}

for folder in CONTENT_DIRS:
    base = ROOT / folder
    if not base.exists():
        continue
    for p in base.rglob("*.md"):
        # skip templates / ignored
        if "08_Templates" in p.parts or p.name.endswith(".ignore"):
            continue

        fm, body = parse_file_with_body(p)
        ntype = fm.get("type", "page")
        name = fm.get("name") or p.stem
        nid = fm.get("id") or f"bb:{ntype}:{slugify(p.stem)}"

        node = {
            "id": nid,
            "type": ntype,
            "name": name,
            "tags": fm.get("tags", []),
            "source": str(p.relative_to(ROOT)),
            "fm": fm,  # full front-matter for UI
            "body_excerpt": (body.strip()[:800] + ("…" if len(body.strip()) > 800 else "")),
            # also mirror only common fields for quick debugging
            "raw": {k: fm.get(k) for k in [
                "parent_location","location","city","faction","factions",
                "allies","rivals","enemies",
                "participants","appears_in","leaders","controls"
            ] if k in fm}
        }
        nodes.append(node)
        nodes_by_id[nid] = node
        name_to_id[name.lower()] = nid
        for aka in as_list(fm.get("aliases")):
            if isinstance(aka, str):
                name_to_id[aka.lower()] = nid

# fold aliases.yaml entries into lookup (name → id)
for k, v in aliases_map.items():
    if isinstance(k, str) and isinstance(v, str):
        name_to_id[k.lower()] = v

def resolve(ref: str | None) -> str | None:
    """
    Resolve a reference which may be:
      - canonical id (already 'bb:...') present in nodes_by_id
      - an alias id from aliases_map values
      - a name found in name_to_id (case-insensitive)
    Return canonical id or None.
    """
    if not isinstance(ref, str):
        return None
    val = ref.strip()
    if not val:
        return None
    # direct node id
    if val in nodes_by_id:
        return val
    # if the alias map already points to an id, accept it
    if val in aliases_map.values() and val in nodes_by_id:
        return val
    # name → id via lookup
    hit = name_to_id.get(val.lower())
    return hit if hit in nodes_by_id else None

# ------------------------
# Pass 2: build edges
# ------------------------
edges: list[dict] = []

def add_edge(src: str | None, rel: str, tgt: str | None):
    if src and tgt and src != tgt:
        edges.append({"source": src, "rel": rel, "target": tgt})

# Structured relationships from fields
for n in nodes:
    src = n["id"]
    fm = n.get("fm", {})

    # Locations → located_in
    for key in ("parent_location", "location", "city"):
        for v in as_list(fm.get(key)):
            rid = resolve(v) if isinstance(v, str) else None
            if rid:
                add_edge(src, "located_in", rid)

    # Factions/Organizations → member_of
    if isinstance(fm.get("faction"), str):
        rid = resolve(fm["faction"])
        if rid:
            add_edge(src, "member_of", rid)
    for v in as_list(fm.get("factions")):
        rid = resolve(v) if isinstance(v, str) else None
        if rid:
            add_edge(src, "member_of", rid)

    # Allies/Rivals/Enemies
    for key, rel in (("allies","ally_of"), ("rivals","rival_of"), ("enemies","enemy_of")):
        for v in as_list(fm.get(key)):
            rid = resolve(v) if isinstance(v, str) else None
            if rid:
                add_edge(src, rel, rid)

# Story/Event participants → appears_in (participant → story)
for n in nodes:
    if n["type"] in {"story", "event"}:
        story_id = n["id"]
        for v in as_list(n["fm"].get("participants")):
            rid = resolve(v) if isinstance(v, str) else None
            if rid:
                add_edge(rid, "appears_in", story_id)

# Direct appears_in list on any node (node → story/event)
for n in nodes:
    for v in as_list(n["fm"].get("appears_in")):
        rid = resolve(v) if isinstance(v, str) else None
        if rid:
            add_edge(n["id"], "appears_in", rid)

# Faction/Org leaders → leads (npc → faction/org)
for n in nodes:
    if n["type"] in {"faction", "organization"}:
        fid = n["id"]
        for v in as_list(n["fm"].get("leaders")):
            rid = resolve(v) if isinstance(v, str) else None
            if rid:
                add_edge(rid, "leads", fid)

# Faction/Org controls → controls (faction/org → location)
for n in nodes:
    if n["type"] in {"faction", "organization"}:
        fid = n["id"]
        for v in as_list(n["fm"].get("controls")):
            rid = resolve(v) if isinstance(v, str) else None
            if rid:
                add_edge(fid, "controls", rid)

# ------------------------
# Emit
# ------------------------
node_ids = {n["id"] for n in nodes}
unresolved = [e for e in edges if e["source"] not in node_ids or e["target"] not in node_ids]

graph = {
    "nodes": nodes,
    "edges": edges,
    "unresolved": unresolved,
    "stats": {
        "nodes": len(nodes),
        "edges": len(edges)
    }
}

out_path = OUT_DIR / "graph.json"
out_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[indexer] nodes={len(nodes)} edges={len(edges)} unresolved={len(unresolved)} → {out_path}")
