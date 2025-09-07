#!/usr/bin/env python3
# indexer.py — builds docs/graph.json (now with appears_in, leads, controls)
import pathlib, re, yaml, json

ROOT = pathlib.Path(__file__).parent
CONTENT_DIRS = ["RPG_Knowledge_Base"]
ALIAS_FILE = ROOT / "aliases" / "aliases.yaml"
OUT = ROOT / "docs"
OUT.mkdir(exist_ok=True, parents=True)

FRONTMATTER = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

def parse_file(p: pathlib.Path):
    text = p.read_text(encoding="utf-8", errors="ignore")
    m = FRONTMATTER.match(text)
    if m:
        try:
            return yaml.safe_load(m.group(1)) or {}
        except Exception:
            return {}
    else:
        try:
            data = yaml.safe_load(text) or {}
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

def slugify(stem): return stem.replace('_','-').replace(' ','-').lower()
def as_list(x): 
    if x is None: return []
    return x if isinstance(x, list) else [x]

# Load aliases
aliases = {}
if ALIAS_FILE.exists():
    try:
        aliases_doc = yaml.safe_load(ALIAS_FILE.read_text(encoding="utf-8")) or {}
        aliases = aliases_doc.get("aliases", {}) or {}
    except Exception:
        pass

# Pass 1: collect nodes
nodes, nodes_by_id, name_to_id = [], {}, {}
for folder in CONTENT_DIRS:
    for p in ROOT.joinpath(folder).rglob("*.md"):
        # skip any *.ignore files or template folders
        if p.suffix == ".ignore" or "08_Templates" in p.parts:
            continue
        data = parse_file(p)
        ntype = data.get("type", "page")
        name  = data.get("name") or p.stem
        nid   = data.get("id") or f"bb:{ntype}:{slugify(p.stem)}"
        node = {
            "id": nid, "type": ntype, "name": name,
            "tags": data.get("tags", []), "source": str(p.relative_to(ROOT)),
            # expose raw fields (handy for debugging)
            "raw": {k: data.get(k) for k in [
                "parent_location","location","city","faction","factions",
                "allies","rivals","enemies","participants","appears_in",
                "leaders","controls"
            ] if k in data}
        }
        nodes.append(node)
        nodes_by_id[nid] = node
        name_to_id[name.lower()] = nid
        for aka in as_list(data.get("aliases")):
            if isinstance(aka, str):
                name_to_id[aka.lower()] = nid

# fold aliases.yaml into lookup
for k, v in aliases.items():
    if isinstance(k, str) and isinstance(v, str):
        name_to_id[k.lower()] = v

def resolve(s):
    if not isinstance(s, str): return None
    s = s.strip()
    if s in nodes_by_id: return s
    if s in aliases.values(): return s
    hit = name_to_id.get(s.lower())
    return hit

# Pass 2: build edges
edges = []
def add_edge(src, rel, tgt):
    if src and tgt and src != tgt:
        edges.append({"source": src, "rel": rel, "target": tgt})

for n in nodes:
    src = n["id"]
    data_fields = n.get("raw", {})

    # locations
    for key in ["parent_location","location","city"]:
        for v in as_list(data_fields.get(key)):
            rid = resolve(v) if isinstance(v,str) else None
            if rid: add_edge(src, "located_in", rid)

    # factions / organizations
    if isinstance(data_fields.get("faction"), str):
        rid = resolve(data_fields["faction"])
        if rid: add_edge(src, "member_of", rid)
    for v in as_list(data_fields.get("factions")):
        rid = resolve(v) if isinstance(v,str) else None
        if rid: add_edge(src, "member_of", rid)

    # allies / rivals / enemies
    for key, rel in [("allies","ally_of"), ("rivals","rival_of"), ("enemies","enemy_of")]:
        for v in as_list(data_fields.get(key)):
            rid = resolve(v) if isinstance(v,str) else None
            if rid: add_edge(src, rel, rid)

# NEW: participants (on stories/events) → appears_in edges
for n in nodes:
    if n["type"] in {"story","event"}:
        src_story = n["id"]
        parts = as_list(n.get("raw", {}).get("participants"))
        for v in parts:
            rid = resolve(v) if isinstance(v,str) else None
            if rid: add_edge(rid, "appears_in", src_story)

# NEW: appears_in (directly on nodes) → appears_in edges
for n in nodes:
    apps = as_list(n.get("raw", {}).get("appears_in"))
    for v in apps:
        rid = resolve(v) if isinstance(v,str) else None
        if rid: add_edge(n["id"], "appears_in", rid)

# NEW: leaders (on factions/orgs) → leads edges (npc → faction)
for n in nodes:
    if n["type"] in {"faction","organization"}:
        fid = n["id"]
        for v in as_list(n.get("raw", {}).get("leaders")):
            rid = resolve(v) if isinstance(v,str) else None
            if rid: add_edge(rid, "leads", fid)

# NEW: controls (on factions/orgs) → controls edges (faction → location)
for n in nodes:
    if n["type"] in {"faction","organization"}:
        fid = n["id"]
        for v in as_list(n.get("raw", {}).get("controls")):
            rid = resolve(v) if isinstance(v,str) else None
            if rid: add_edge(fid, "controls", rid)

# Emit graph + basic unresolved list (for reference)
node_ids = {n["id"] for n in nodes}
unresolved = []
for e in edges:
    if e["source"] not in node_ids or e["target"] not in node_ids:
        unresolved.append(e)

graph = {"nodes": nodes, "edges": edges, "unresolved": unresolved}
(OUT / "graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[indexer] nodes={len(nodes)} edges={len(edges)} unresolved={len(unresolved)} → docs/graph.json")
