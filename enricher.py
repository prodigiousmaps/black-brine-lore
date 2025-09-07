#!/usr/bin/env python3
# enricher.py — propose relations + normalize fields, now with participants/leaders/controls
import pathlib, re, json, yaml
from collections import defaultdict, Counter

ROOT = pathlib.Path(__file__).parent
SRC_DIRS = ["RPG_Knowledge_Base"]
IGNORE_DIRS = {"08_Templates"}
DOCS_DIR = ROOT / "docs"
PATCH_DIR = ROOT / "patches"
ALIAS_FILE = ROOT / "aliases" / "aliases.yaml"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
PATCH_DIR.mkdir(parents=True, exist_ok=True)

FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

def read_front_matter(p: pathlib.Path):
    text = p.read_text(encoding="utf-8", errors="ignore")
    m = FM_RE.match(text)
    data, body = {}, ""
    if m:
        try: data = yaml.safe_load(m.group(1)) or {}
        except Exception: data = {}
        body = text[m.end():]
    else:
        try: data = yaml.safe_load(text) or {}
        except Exception: data = {}
        body = ""
    return data if isinstance(data, dict) else {}, body

def file_iter():
    for folder in SRC_DIRS:
        for p in ROOT.joinpath(folder).rglob("*.md"):
            if "08_Templates" in p.parts or p.name.endswith(".ignore"): continue
            yield p

def as_list(x): 
    if x is None: return []
    return x if isinstance(x, list) else [x]

# Optional fuzzy
try:
    from rapidfuzz import process, fuzz
    HAVE_FUZZ=True
except Exception:
    HAVE_FUZZ=False

# Load aliases + build gazetteer
aliases = {}
if ALIAS_FILE.exists():
    ad = yaml.safe_load(ALIAS_FILE.read_text(encoding="utf-8")) or {}
    aliases = ad.get("aliases", {}) or {}

nodes = []
name_to_id, id_to_name = {}, {}
files = {}

for p in file_iter():
    fm, body = read_front_matter(p)
    files[str(p)] = (fm, body)
    ntype = fm.get("type","page")
    name  = fm.get("name") or p.stem
    nid   = fm.get("id") or f"bb:{ntype}:{re.sub(r'[^a-z0-9\-]+','-',(p.stem.lower().replace(' ','-'))).strip('-')}"
    nodes.append({"id":nid,"name":name,"type":ntype,"path":str(p.relative_to(ROOT))})
    id_to_name[nid]=name
    name_to_id[name.lower()]=nid
    for aka in as_list(fm.get("aliases")):
        if isinstance(aka,str): name_to_id[aka.lower()]=nid

for k,v in aliases.items():
    if isinstance(k,str) and isinstance(v,str): name_to_id[k.lower()]=v

def resolve(val: str):
    if not isinstance(val,str): return (None,"none",0.0)
    v=val.strip()
    if v in id_to_name: return (v,"id",1.0)
    cid = name_to_id.get(v.lower())
    if cid: return (cid,"alias",1.0)
    if HAVE_FUZZ:
        choices = list(name_to_id.keys())
        match = process.extractOne(v.lower(), choices, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= 90: return (name_to_id[match[0]],"fuzzy",match[1]/100.0)
    return (None,"none",0.0)

PHRASES = [
    (re.compile(r'\b(rival|rivals|rivalry|at war with|feud(?:s)? with)\b', re.I), "rival_of"),
    (re.compile(r'\b(ally|allies|alliance with|supported by|aided by)\b', re.I), "ally_of"),
    (re.compile(r'\b(enemy|enemies|opposed by|hunted by)\b', re.I), "enemy_of"),
    (re.compile(r'\b(controls|dominates|rules)\b', re.I), "controls"),
    (re.compile(r'\b(leader|leads|headed by|captained by)\b', re.I), "leads"),
]

def find_names_simple(text: str):
    return re.findall(r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3})\b', text or "")

suggestions = []
by_file = defaultdict(list)
def add(path, kind, field, value, rid, method, score, note=""):
    s={"path":path,"kind":kind,"field":field,"value":value,"resolved_id":rid,"method":method,"score":round(float(score),3),"note":note}
    suggestions.append(s); by_file[path].append(s)

REL_FIELDS = [
    ("location","located_in"),
    ("parent_location","located_in"),
    ("city","located_in"),
    ("faction","member_of"),
    ("factions","member_of"),
    ("allies","ally_of"),
    ("rivals","rival_of"),
    ("enemies","enemy_of"),
    # NEW direct-list fields we want to encourage via patches:
    ("appears_in","appears_in"),
    ("leaders","leads"),
    ("controls","controls"),
    ("participants","appears_in@story"),  # special: lives on story/event
]

for path, (fm, body) in files.items():
    src_type = fm.get("type","page")
    src_id = fm.get("id") or f"bb:{src_type}:{re.sub(r'[^a-z0-9\-]+','-',(pathlib.Path(path).stem.lower().replace(' ','-'))).strip('-')}"

    # 1) structured fields
    for field, rel in REL_FIELDS:
        vals = as_list(fm.get(field))
        for v in vals:
            if not isinstance(v,str): continue
            rid, method, score = resolve(v)
            if rel == "appears_in@story":
                # participants live on stories; just validate they resolve
                if src_type in {"story","event"} and rid:
                    add(path, "relation", "participants→appears_in", v, rid, method, score, "story participants")
            else:
                if rid: add(path, "relation", rel, v, rid, method, score)
                else:   add(path, "unresolved", field, v, None, "none", 0, "add to aliases.yaml or create node")

    # 2) phrasebook finds (summary/body)
    text = f"{fm.get('summary','')}\n{body or ''}"
    if text.strip():
        mentioned = Counter(find_names_simple(text))
        for rx, rel in PHRASES:
            if rx.search(text):
                for name, _ in mentioned.most_common(3):
                    rid, method, score = resolve(name)
                    if rid and rid != src_id:
                        add(path, "relation", rel, name, rid, f"phrase+{method}", score)

# Build patches (normalize to ids; add list fields if confidently inferred)
AUTO_THRESH = 0.92
def confident(meth, score, rel):
    if meth in {"id","alias"}: return True
    if meth.startswith("phrase+"): return score >= 0.96 and rel in {"ally_of","rival_of","enemy_of","controls","leads"}
    return score >= AUTO_THRESH

patch_manifest = []
for path, items in by_file.items():
    fm, _ = files[path]
    patch = {"path": path, "set": {}}
    changed = False

    # Normalize structured fields to ids
    for fld in ("location","parent_location","city"):
        vals = as_list(fm.get(fld))
        if not vals: continue
        out, touched = [], False
        for v in vals:
            if not isinstance(v,str): continue
            rid, meth, score = resolve(v)
            if rid: 
                out.append(rid); 
                if meth != "id": touched = True
            else:
                out.append(v)
        if out and touched:
            patch["set"][fld] = out[0] if len(out)==1 else out
            changed = True

    # factions → ids (collapsed into one 'factions' list)
    fvals = as_list(fm.get("faction")) + as_list(fm.get("factions"))
    if fvals:
        out, touched = [], False
        for v in fvals:
            if not isinstance(v,str): continue
            rid, meth, score = resolve(v)
            if rid:
                out.append(rid); 
                if meth != "id": touched = True
            else:
                out.append(v)
        if out and touched:
            patch["set"]["factions"] = sorted(set(out)); changed = True

    # NEW: leaders/controls/appears_in lists (add if confidently inferred by names or already ids)
    for fld in ("leaders","controls","appears_in"):
        vals = as_list(fm.get(fld))
        # integrate any high-confidence relations from suggestions
        add_ins = []
        for s in items:
            if s["kind"]=="relation" and s["resolved_id"] and s["field"] in { "leaders" if fld=="leads" else fld, ("appears_in" if fld=="appears_in" else fld)}:
                if confident(s["method"], s["score"], s["field"]):
                    add_ins.append(s["resolved_id"])
        merged = sorted(set([v for v in vals if isinstance(v,str)] + add_ins))
        if merged and merged != vals:
            patch["set"][fld] = merged; changed = True

    # participants live on stories; we don’t auto-add them unless already present (we validate only)

    if changed and patch["set"]:
        outp = PATCH_DIR / (re.sub(r'[^a-z0-9\-]+','-', pathlib.Path(path).stem.lower()) + ".yml")
        outp.write_text(yaml.safe_dump(patch, sort_keys=False, allow_unicode=True), encoding="utf-8")
        patch_manifest.append(str(outp.relative_to(ROOT)))

(DOCS_DIR / "suggestions.json").write_text(json.dumps({"patches": patch_manifest, "count": len(suggestions), "suggestions": suggestions}, ensure_ascii=False, indent=2), encoding="utf-8")

# Light-weight report
REPORT = """<!doctype html><meta charset="utf-8"><title>Enrichment Report</title>
<style>body{font:14px/1.5 system-ui,sans-serif;background:#0a0a0b;color:#e8e8ea;margin:18px}
h1{font-size:22px;margin:0 0 8px} table{width:100%;border-collapse:collapse}
td,th{border-bottom:1px solid #2a2d36;padding:6px 8px;text-align:left;font-size:13px}
.small{opacity:.8} code{background:#111215;padding:1px 4px;border-radius:4px}</style>
<h1>Enrichment Suggestions</h1>
<div class="small">participants→appears_in • leaders→leads • controls→controls now supported.</div>
<table><thead><tr><th>File</th><th>Kind</th><th>Field</th><th>Value</th><th>Resolved</th><th>Method</th><th>Score</th></tr></thead><tbody id="tb"></tbody></table>
<script>
fetch('suggestions.json').then(r=>r.json()).then(d=>{
  const tb=document.getElementById('tb');
  d.suggestions.forEach(s=>{
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${s.path.replace(/^.*RPG_Knowledge_Base\\//,'')}</td>
      <td>${s.kind}</td><td>${s.field}</td><td><code>${(s.value||'').toString().replace(/</g,'&lt;')}</code></td>
      <td>${s.resolved_id||'—'}</td><td>${s.method}</td><td>${(s.score||0).toFixed(2)}</td>`;
    tb.appendChild(tr);
  });
});
</script>"""
(DOCS_DIR / "report.html").write_text(REPORT, encoding="utf-8")

print("[enricher] done → docs/suggestions.json, docs/report.html, patches/")
