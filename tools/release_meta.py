#!/usr/bin/env python3
"""Validate clawmain release metadata.

Checks:
  - marketplace metadata.version is semver and has a "## X.Y.Z" section in CHANGELOG.md
  - every marketplace plugin entry version matches that plugin's plugin.json
  - with --check-bumps (needs full git history): any plugin whose files changed since the
    last release tag has a new version, and so does the marketplace

Prints `version=X.Y.Z` and `tag=vX.Y.Z` lines (GitHub Actions $GITHUB_OUTPUT format).

Usage:
  python tools/release_meta.py [--check-bumps]
  python tools/release_meta.py --notes     print the CHANGELOG section for the current version
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ".claude-plugin/marketplace.json"
SEMVER = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?")


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def load_json(text: str) -> dict:
    return json.loads(text) if text else {}


def plugin_versions(marketplace: dict, read) -> dict[str, tuple[str, str | None]]:
    """name -> (marketplace entry version, plugin.json version) using `read(relpath)`."""
    out = {}
    for entry in marketplace.get("plugins", []):
        source = entry["source"].removeprefix("./")
        manifest = load_json(read(f"{source}/.claude-plugin/plugin.json"))
        out[entry["name"]] = (entry.get("version", ""), manifest.get("version"))
    return out


def changelog_section(version: str) -> str:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(version)}\b.*?$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def check_bumps(version: str, marketplace: dict) -> list[str]:
    tags = [t for t in git("tag", "--list", "v*", "--sort=-v:refname").splitlines() if t]
    if not tags:
        return []
    released = f"v{version}" in tags
    base = f"v{version}" if released else tags[0]
    old_marketplace = load_json(git("show", f"{base}:{MARKETPLACE}"))
    old = plugin_versions(old_marketplace, lambda p: git("show", f"{base}:{p}"))
    errors = []
    changed_any = False
    for entry in marketplace.get("plugins", []):
        name, source = entry["name"], entry["source"].removeprefix("./")
        if not git("diff", "--name-only", base, "HEAD", "--", source):
            continue
        changed_any = True
        if released:
            errors.append(f"{name}: changed after {base} was released; bump it (python tools/bump.py {name} patch)")
        elif name in old and old[name][1] == entry.get("version"):
            errors.append(f"{name}: changed since {base} but still version {entry.get('version')}; bump it")
    if changed_any and not released and old_marketplace.get("metadata", {}).get("version") == version:
        errors.append(f"marketplace: plugins changed since {base} but metadata.version is still {version}")
    return errors


def main(argv: list[str]) -> int:
    marketplace = json.loads((ROOT / MARKETPLACE).read_text(encoding="utf-8"))
    version = marketplace.get("metadata", {}).get("version", "")
    if "--notes" in argv:
        print(changelog_section(version) or f"clawmain {version}")
        return 0

    errors = []
    if not SEMVER.fullmatch(version):
        errors.append(f"marketplace metadata.version '{version}' is not semver")
    if not changelog_section(version) and f"## {version}" not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
        errors.append(f"CHANGELOG.md has no '## {version}' section")
    for name, (listed, manifest) in plugin_versions(
        marketplace, lambda p: (ROOT / p).read_text(encoding="utf-8") if (ROOT / p).exists() else ""
    ).items():
        if manifest is None:
            errors.append(f"{name}: plugin.json missing")
        elif listed != manifest:
            errors.append(f"{name}: marketplace lists {listed} but plugin.json says {manifest}")
        elif not SEMVER.fullmatch(manifest):
            errors.append(f"{name}: version '{manifest}' is not semver")
    if "--check-bumps" in argv:
        errors += check_bumps(version, marketplace)

    if errors:
        print("release metadata invalid:\n  " + "\n  ".join(errors), file=sys.stderr)
        return 1
    print(f"version={version}")
    print(f"tag=v{version}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
