#!/usr/bin/env python3
"""
apply_patches.py — Apply patches/*.yml to source markdown front-matter.

Usage:
  py -3.13 apply_patches.py            # apply all patches
  py -3.13 apply_patches.py --dry      # show what would change
"""
import pathlib, yaml, re, sys

ROOT = pathlib.Path(__file__).parent
PATCH_DIR = ROOT / "patches"
FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

def read_fm_and_body(p: pathlib.Path):
    text = p.read_text(encoding="utf-8", errors="ignore")
    m = FM_RE.match(text)
    if m:
        fm = yaml.safe_load(m.group(1)) or {}
        body = text[m.end():]
    else:
        fm = {}
        body = text
    if not isinstance(fm, dict): fm = {}
    return fm, body

def write_fm_and_body(p: pathlib.Path, fm: dict, body: str):
    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True)
    out = f"---\n{fm_text}---\n{body}"
    p.write_text(out, encoding="utf-8")

def main():
    dry = "--dry" in sys.argv
    patches = sorted(PATCH_DIR.glob("*.yml"))
    if not patches:
        print("[apply_patches] no patches found.")
        return
    for pp in patches:
        patch = yaml.safe_load(pp.read_text(encoding="utf-8")) or {}
        path = patch.get("path")
        sets = patch.get("set", {})
        if not path or not sets:
            continue
        src = ROOT / path
        if not src.exists():
            print(f"[apply_patches] missing source: {src}")
            continue
        fm, body = read_fm_and_body(src)
        changed = False
        for k, v in sets.items():
            if fm.get(k) != v:
                fm[k] = v
                changed = True
        if changed:
            if dry:
                print(f"[apply_patches] would update: {src}  fields: {', '.join(sets.keys())}")
            else:
                write_fm_and_body(src, fm, body)
                print(f"[apply_patches] updated: {src}  fields: {', '.join(sets.keys())}")

if __name__ == "__main__":
    main()
