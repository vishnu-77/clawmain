"""End-to-end smoke for the clawmain marketplace in a real Claude Code CLI.

Uses an isolated CLAUDE_CONFIG_DIR so the user's own setup is never touched. Adds this
checkout as a marketplace, installs every plugin it lists, and checks with
`claude plugin details` that Claude Code loaded exactly the skills and agents on disk,
at the listed version, within the always-on token budget.

Usage: python scripts/smoke_plugins.py [--max-always-on TOKENS] [--source PATH_OR_REPO]
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_ALWAYS_ON = 1500  # tokens each plugin may add to every session


def arg(argv: list[str], flag: str, default: str) -> str:
    return argv[argv.index(flag) + 1] if flag in argv else default


def parse_tokens(text: str) -> int:
    match = re.search(r"Always-on:\s*~?([\d.]+)\s*(k?)\s*tok", text)
    if not match:
        return -1
    value = float(match.group(1)) * (1000 if match.group(2) else 1)
    return int(value)


def parse_names(text: str, label: str) -> list[str]:
    match = re.search(rf"^\s*{label} \((\d+)\)[ \t]*(.*)$", text, re.MULTILINE)
    if not match:
        return []
    names = [n.strip() for n in match.group(2).split(",") if n.strip()]
    assert len(names) == int(match.group(1)), (label, match.group(0))
    return sorted(names)


def main(argv: list[str]) -> int:
    claude = shutil.which("claude")
    assert claude, "Claude Code CLI not found on PATH (npm install -g @anthropic-ai/claude-code)"
    max_always_on = int(arg(argv, "--max-always-on", str(DEFAULT_MAX_ALWAYS_ON)))
    source = arg(argv, "--source", str(ROOT))

    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    market_name = marketplace["name"]
    config = Path(tempfile.mkdtemp(prefix="clawmain-smoke-"))
    env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config), "DISABLE_AUTOUPDATER": "1"}

    def run(*args: str) -> str:
        result = subprocess.run([claude, *args], capture_output=True, env=env, cwd=ROOT,
                                timeout=180, check=False)
        out = result.stdout.decode(errors="replace") + result.stderr.decode(errors="replace")
        assert result.returncode == 0, (args, out)
        return out

    failures: list[str] = []
    rows: list[tuple[str, str, int, int, int]] = []
    try:
        run("plugin", "marketplace", "add", source)
        for entry in marketplace["plugins"]:
            name = entry["name"]
            plugin_dir = ROOT / entry["source"].removeprefix("./")
            run("plugin", "install", f"{name}@{market_name}")
            details = run("plugin", "details", f"{name}@{market_name}")

            want_skills = sorted(p.parent.name for p in plugin_dir.glob("skills/*/SKILL.md"))
            want_agents = sorted(p.stem for p in plugin_dir.glob("agents/*.md"))
            got_skills = parse_names(details, "Skills")
            got_agents = parse_names(details, "Agents")
            tokens = parse_tokens(details)

            if f"({name}) {entry['version']}" not in details:
                failures.append(f"{name}: loaded version does not match {entry['version']}")
            if got_skills != want_skills:
                failures.append(f"{name}: skills loaded {got_skills}, expected {want_skills}")
            if got_agents != want_agents:
                failures.append(f"{name}: agents loaded {len(got_agents)}, expected {len(want_agents)}; "
                                f"missing {sorted(set(want_agents) - set(got_agents))}")
            if tokens < 0:
                failures.append(f"{name}: could not read always-on token cost")
            elif tokens > max_always_on:
                failures.append(f"{name}: always-on cost ~{tokens} tok exceeds budget {max_always_on}")
            rows.append((name, entry["version"], len(got_skills), len(got_agents), tokens))
    finally:
        shutil.rmtree(config, ignore_errors=True)

    print(f"{'plugin':<16} {'version':<8} {'skills':>6} {'agents':>6} {'always-on':>10}")
    for name, version, skills, agents, tokens in rows:
        print(f"{name:<16} {version:<8} {skills:>6} {agents:>6} {('~' + str(tokens) + ' tok'):>10}")
    total_agents = sum(r[3] for r in rows)
    print(f"{len(rows)} plugins, {total_agents} agents loaded")
    if failures:
        print("SMOKE FAILED:\n  " + "\n  ".join(failures), file=sys.stderr)
        return 1
    print("SMOKE OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
