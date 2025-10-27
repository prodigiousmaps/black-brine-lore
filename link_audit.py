#!/usr/bin/env python3
"""
Black Brine Lore Link Auditor & Auto-Linker
-------------------------------------------
Scans YAML lore nodes for missing or one-way connections
and ensures bidirectional linking between related entities.

Usage:
    python link_audit.py ./lore --write

Without `--write`, it runs in audit-only mode.
"""

import yaml
import argparse
from pathlib import Path
from collections import defaultdict

# ----------------------------------------
# Utility: Safe YAML Loader/Dumper
# ----------------------------------------
def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_yaml(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=1000)

# ----------------------------------------
# Relation heuristics
# ----------------------------------------
def infer_relation(source_type, target_type):
    if source_type == "npc" and target_type == "location":
        return "present_at"
    if source_type == "story" and target_type == "location":
        return "involves"
    if source_type == "location" and target_type == "npc":
        return "inhabited_by"
    if source_type == "creature" and target_type == "location":
        return "haunts"
    if source_type == "npc" and target_type == "npc":
        return "knows"
    return "linked"

# ----------------------------------------
# Core Logic
# ----------------------------------------
def main(lore_path, write=False):
    lore_dir = Path(lore_path)
    if not lore_dir.exists():
        print(f"❌ Lore folder not found: {lore_path}")
        return

    files = list(lore_dir.rglob("*.yml")) + list(lore_dir.rglob("*.yaml"))
    index = {}
    reverse_refs = defaultdict(list)
    report = []

    # Pass 1: Index all nodes
    for f in files:
        try:
            doc = load_yaml(f)
            if not isinstance(doc, dict) or "id" not in doc:
                continue
            index[doc["id"]] = {"path": f, "doc": doc}
        except Exception as e:
            print(f"⚠️ Could not parse {f}: {e}")

    # Pass 2: Build reverse lookup for existing connections
    for node_id, entry in index.items():
        doc = entry["doc"]
        if "connections" in doc:
            for c in doc["connections"]:
                target = c.get("linked_to")
                if target:
                    reverse_refs[target].append(node_id)

    # Pass 3: Auto-link detection and correction
    for node_id, entry in index.items():
        doc = entry["doc"]
        node_type = doc.get("type", "unknown")
        changed = False

        # 3a. Parent and appears_in
        parent = doc.get("parent_location")
        appears = doc.get("appears_in", [])

        inferred_targets = set()
        if parent:
            inferred_targets.add(parent)
        for a in appears:
            inferred_targets.add(a)

        # 3b. Connections block init
        if "connections" not in doc:
            doc["connections"] = []

        existing_targets = {c.get("linked_to") for c in doc["connections"] if c.get("linked_to")}

        # Add missing connections based on parent/appears_in
        for target_id in inferred_targets:
            if target_id not in index:
                continue
            if target_id not in existing_targets:
                relation = infer_relation(node_type, index[target_id]["doc"].get("type"))
                doc["connections"].append({"linked_to": target_id, "relation": relation})
                report.append(f"🧩 Added connection: {node_id} → {target_id} ({relation})")
                changed = True

        # 3c. Ensure bidirectional links
        for c in doc["connections"]:
            target = c.get("linked_to")
            if not target or target not in index:
                continue
            target_doc = index[target]["doc"]
            if "connections" not in target_doc:
                target_doc["connections"] = []
            if not any(x.get("linked_to") == node_id for x in target_doc["connections"]):
                reverse_relation = infer_relation(target_doc.get("type"), node_type)
                target_doc["connections"].append({"linked_to": node_id, "relation": reverse_relation})
                report.append(f"↔️ Added reverse link: {target} → {node_id} ({reverse_relation})")
                changed = True

        if changed and write:
            save_yaml(entry["path"], doc)

    # Write back modified targets if needed
    if write:
        for target_id, entry in index.items():
            save_yaml(entry["path"], entry["doc"])

    # Final report
    print("\n===== LINK AUDIT REPORT =====")
    if report:
        for line in report:
            print(line)
    else:
        print("✅ All nodes already fully linked.")
    print("==============================")

# ----------------------------------------
# CLI Entrypoint
# ----------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Black Brine Lore Link Auditor")
    parser.add_argument("path", help="Path to lore directory")
    parser.add_argument("--write", action="store_true", help="Write changes to files")
    args = parser.parse_args()
    main(args.path, write=args.write)
