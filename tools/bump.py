#!/usr/bin/env python3
"""Bump plugin versions and the marketplace version.

Usage:
  python tools/bump.py <plugin> [patch|minor|major]   bump one plugin (+ marketplace patch)
  python tools/bump.py all [patch|minor|major]        bump every plugin (+ marketplace same level)
  python tools/bump.py marketplace [patch|minor|major]

Department plugins are bumped in catalog/<slug>.toml, then tools/build.py regenerates.
Hand-written plugins (groundwork) are bumped in their plugin.json and marketplace entry.
Add a "## X.Y.Z" section to CHANGELOG.md afterwards.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
LEVELS = ("patch", "minor", "major")


def bumped(version: str, level: str) -> str:
    major, minor, patch = (int(p) for p in version.split("-")[0].split("+")[0].split("."))
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def bump_catalog(slug: str, level: str) -> str:
    path = ROOT / "catalog" / f"{slug}.toml"
    text = path.read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', text.split("[[agents]]")[0], re.MULTILINE)
    old = match.group(1) if match else "0.1.0"
    new = bumped(old, level)
    if match:
        text = text.replace(match.group(0), f'version = "{new}"', 1)
    else:
        text = re.sub(r'^(slug = "[^"]+")$', rf'\1\nversion = "{new}"', text, count=1, flags=re.MULTILINE)
    path.write_text(text, encoding="utf-8", newline="\n")
    return f"{slug} {old} -> {new}"


def bump_manual(entry: dict, level: str) -> str:
    manifest_path = ROOT / entry["source"].removeprefix("./") / ".claude-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    old = manifest["version"]
    manifest["version"] = entry["version"] = bumped(old, level)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return f"{entry['name']} {old} -> {manifest['version']}"


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    target = argv[1]
    level = argv[2] if len(argv) > 2 else "patch"
    if level not in LEVELS:
        print(f"level must be one of {LEVELS}")
        return 1

    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    entries = {e["name"]: e for e in data["plugins"]}
    if target not in entries and target not in ("all", "marketplace"):
        print(f"unknown plugin '{target}'; known: {', '.join(entries)}")
        return 1

    names = list(entries) if target == "all" else [] if target == "marketplace" else [target]
    notes = []
    for name in names:
        if (ROOT / "catalog" / f"{name}.toml").exists():
            notes.append(bump_catalog(name, level))
        else:
            notes.append(bump_manual(entries[name], level))

    market_level = level if target in ("all", "marketplace") else "patch"
    old = data["metadata"]["version"]
    data["metadata"]["version"] = bumped(old, market_level)
    MARKETPLACE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    notes.append(f"marketplace {old} -> {data['metadata']['version']}")

    subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], check=True)
    print("\n".join(notes))
    print(f"next: add '## {data['metadata']['version']}' to CHANGELOG.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
