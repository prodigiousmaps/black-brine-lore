#!/usr/bin/env python3
import pathlib, re, yaml, json, sys

ROOT = pathlib.Path(__file__).parent
CONTENT_DIRS = ["RPG_Knowledge_Base"]  # adjust if your folder is named differently
ALIAS_FILE = ROOT / "aliases" / "aliases.yaml"
OUT = ROOT / "public"
OUT.mkdir(exist_ok=True, parents=True)

FRONTMATTER = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

def parse_file(p: pathlib.Path):
    text = p.read_text(encoding="utf-8", errors="ignore")
    m = FRONTMATTER.match(text)
    if m:
        data = yaml.safe_load(m.group(1)) or {}
    else:
        try:
            data = yaml.safe_load(text) or {}
        except Exception:
            data = {}
    if not isinstance(data, dict): data = {}
    return data

def slug_name(stem):
    return stem.replace('_','-').replace(' ','-').lower()

def as_list(x):
    if x is None: return []
    return x if isinstance(x, list) else [x]

# Load aliases
aliases = {}
if ALIAS_FILE.exists():
    aliases_doc = yaml.safe_load(ALIAS_FILE.read_text(encoding="utf-8")) or {}
    aliases = aliases_doc.get("aliases", {}) or {}

def resolve(target, nodes_by_id, name_to_id):
    if not target: return None
    # alias string?
    tid = aliases.get(target)
    if tid: return tid
    # direct id?
    if target in nodes_by_id: return target
    # name lookup
    nid = name_to_id.get(target.lower())
    return nid

nodes = []
edges = []
nodes_by_id = {}
name_to_id = {}

# 1) Pass: collect nodes
for folder in CONTENT_DIRS:
    for p in ROOT.joinpath(folder).rglob("*.md"):
        data = parse_file(p)
        ntype = data.get("type", "page")
        name = data.get("name") or p.stem
        nid = data.get("id") or f"bb:{ntype}:{slug_name(p.stem)}"
        node = {
            "id": nid,
            "type": ntype,
            "name": name,
            "tags": data.get("tags", []),
            "source": str(p.relative_to(ROOT))
        }
        # keep some common fields if present
        for k in ["summary","parent_location","location","faction","factions","city","aliases"]:
            if k in data: node[k] = data[k]
        nodes.append(node)
        nodes_by_id[nid] = node
        name_to_id[name.lower()] = nid

# 2) Pass: build edges
def add_edge(src, rel, tgt):
    if src and tgt and src != tgt:
        edges.append({"source": src, "rel": rel, "target": tgt})

for n in nodes:
    src = n["id"]
    # locations
    for key in ["parent_location","location","city"]:
        for v in as_list(n.get(key)):
            if isinstance(v, str):
                add_edge(src, "located_in", v.strip())
    # factions
    f_single = n.get("faction")
    if isinstance(f_single, str): add_edge(src, "member_of", f_single.strip())
    for v in as_list(n.get("factions")):
        if isinstance(v, str): add_edge(src, "member_of", v.strip())
        elif isinstance(v, dict):
            nm = v.get("name") or v.get("faction")
            if nm: add_edge(src, "member_of", nm.strip())

# 3) Resolve targets to canonical IDs
unresolved = []
for e in edges:
    tgt = e["target"]
    if tgt in nodes_by_id:
        continue
    rid = resolve(tgt, nodes_by_id, name_to_id)
    if rid:
        e["target"] = rid
    else:
        unresolved.append(e)

# 4) Emit graph + report
graph = {"nodes": nodes, "edges": edges, "unresolved": unresolved}
(OUT / "graph.json").write_text(json.dumps(graph, ensure_ascii=False), encoding="utf-8")

# 5) Simple human report
print(f"Indexed {len(nodes)} nodes, {len(edges)} edges")
print(f"Unresolved references: {len(unresolved)}")
if unresolved:
    print("Examples:")
    for x in unresolved[:20]:
        print(" -", x["source"], x["rel"], "→", x["target"])
    sys.exit(1)  # non-zero to remind you to add aliases/ids
