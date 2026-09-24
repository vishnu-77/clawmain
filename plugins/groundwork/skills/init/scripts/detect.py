#!/usr/bin/env python3
"""Groundwork stack detector.

Scans a repository and prints a JSON profile: languages, package managers,
candidate commands (with where they came from), key directories, paths agents
should not edit, CI files, and existing agent configuration.

Standard library only. Read-only: never runs project commands.

Usage: python detect.py [repo_path]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11: TOML-based hints are skipped
    tomllib = None

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "target", ".next", ".turbo", ".tox",
}
GENERATED_DIRS = {
    "dist", "build", "out", "target", ".next", "coverage", "htmlcov",
    "vendor", "node_modules", "__generated__", "generated",
}
AGENT_CONFIGS = [
    "AGENTS.md", "CLAUDE.md", "CLAUDE.local.md", ".claude/settings.json",
    ".claude/settings.local.json", ".claude/skills", ".claude/agents",
    ".claude/commands", ".mcp.json", ".cursorrules", ".cursor/rules",
    ".github/copilot-instructions.md", "GEMINI.md",
]
SCRIPT_ROLES = {
    "install": ("install", "setup", "bootstrap"),
    "build": ("build", "compile"),
    "test": ("test", "tests", "check"),
    "lint": ("lint", "typecheck", "type-check", "check-types"),
    "format": ("format", "fmt", "prettier"),
    "run": ("dev", "start", "serve", "run"),
}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(_read_text(path))
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def _read_toml(path: Path) -> dict:
    if tomllib is None:
        return {}
    try:
        return tomllib.loads(_read_text(path))
    except ValueError:  # TOMLDecodeError subclasses ValueError
        return {}


def _role_for(name: str) -> str | None:
    lowered = name.lower()
    for role, words in SCRIPT_ROLES.items():
        if lowered in words or lowered.split(":")[0] in words:
            return role
    return None


def _add(commands: list, role: str, cmd: str, source: str) -> None:
    if not any(c["cmd"] == cmd for c in commands):
        commands.append({"role": role, "cmd": cmd, "source": source})


def detect_node(root: Path, profile: dict) -> None:
    pkg_path = root / "package.json"
    if not pkg_path.exists():
        return
    pkg = _read_json(pkg_path)
    profile["languages"].append("javascript/typescript")
    if (root / "tsconfig.json").exists():
        profile["languages"][-1] = "typescript"

    if (root / "pnpm-lock.yaml").exists():
        pm = "pnpm"
    elif (root / "yarn.lock").exists():
        pm = "yarn"
    elif (root / "bun.lockb").exists() or (root / "bun.lock").exists():
        pm = "bun"
    else:
        pm = "npm"
    profile["package_managers"].append(pm)
    _add(profile["commands"], "install", f"{pm} install", "package.json")

    if pkg.get("workspaces") or (root / "pnpm-workspace.yaml").exists():
        profile["monorepo"] = True
    if (root / "turbo.json").exists() or (root / "nx.json").exists():
        profile["monorepo"] = True

    for name in sorted((pkg.get("scripts") or {})):
        role = _role_for(name)
        if role:
            run = f"{pm} test" if name == "test" and pm != "bun" else f"{pm} run {name}"
            _add(profile["commands"], role, run, "package.json scripts")


def detect_python(root: Path, profile: dict) -> None:
    pyproject = root / "pyproject.toml"
    markers = [pyproject, root / "setup.py", root / "requirements.txt", root / "setup.cfg"]
    if not any(p.exists() for p in markers):
        return
    profile["languages"].append("python")
    data = _read_toml(pyproject) if pyproject.exists() else {}
    tool = data.get("tool", {}) if isinstance(data.get("tool"), dict) else {}

    if (root / "uv.lock").exists() or "uv" in tool:
        pm, prefix = "uv", "uv run "
        _add(profile["commands"], "install", "uv sync", "uv.lock")
    elif (root / "poetry.lock").exists() or "poetry" in tool:
        pm, prefix = "poetry", "poetry run "
        _add(profile["commands"], "install", "poetry install", "poetry.lock")
    else:
        pm, prefix = "pip", ""
        if pyproject.exists():
            _add(profile["commands"], "install", "pip install -e .", "pyproject.toml")
        elif (root / "requirements.txt").exists():
            _add(profile["commands"], "install", "pip install -r requirements.txt", "requirements.txt")
    profile["package_managers"].append(pm)

    has_tests = (root / "tests").is_dir() or (root / "test").is_dir()
    if "pytest" in tool or (root / "pytest.ini").exists() or (root / "conftest.py").exists() or has_tests:
        _add(profile["commands"], "test", f"{prefix}pytest", "pytest config/tests dir")
    if "ruff" in tool or (root / "ruff.toml").exists() or (root / ".ruff.toml").exists():
        _add(profile["commands"], "lint", f"{prefix}ruff check .", "ruff config")
        _add(profile["commands"], "format", f"{prefix}ruff format .", "ruff config")
    if "black" in tool:
        _add(profile["commands"], "format", f"{prefix}black .", "black config")
    if "mypy" in tool or (root / "mypy.ini").exists():
        _add(profile["commands"], "lint", f"{prefix}mypy .", "mypy config")


def detect_other(root: Path, profile: dict) -> None:
    if (root / "go.mod").exists():
        profile["languages"].append("go")
        profile["package_managers"].append("go")
        for role, cmd in (("build", "go build ./..."), ("test", "go test ./..."), ("lint", "go vet ./...")):
            _add(profile["commands"], role, cmd, "go.mod")
    if (root / "Cargo.toml").exists():
        profile["languages"].append("rust")
        profile["package_managers"].append("cargo")
        cargo = _read_toml(root / "Cargo.toml")
        if "workspace" in cargo:
            profile["monorepo"] = True
        for role, cmd in (("build", "cargo build"), ("test", "cargo test"),
                          ("lint", "cargo clippy"), ("format", "cargo fmt")):
            _add(profile["commands"], role, cmd, "Cargo.toml")
    for gradle in ("gradlew", "build.gradle", "build.gradle.kts"):
        if (root / gradle).exists():
            profile["languages"].append("jvm")
            runner = "./gradlew" if (root / "gradlew").exists() else "gradle"
            _add(profile["commands"], "build", f"{runner} build", gradle)
            _add(profile["commands"], "test", f"{runner} test", gradle)
            break
    if (root / "pom.xml").exists():
        profile["languages"].append("jvm")
        _add(profile["commands"], "build", "mvn package", "pom.xml")
        _add(profile["commands"], "test", "mvn test", "pom.xml")


def detect_task_runners(root: Path, profile: dict) -> None:
    makefile = root / "Makefile"
    if makefile.exists():
        for target in re.findall(r"^([A-Za-z][\w-]*):(?!=)", _read_text(makefile), re.MULTILINE):
            role = _role_for(target)
            if role:
                _add(profile["commands"], role, f"make {target}", "Makefile")
    justfile = next((p for p in (root / "justfile", root / "Justfile") if p.exists()), None)
    if justfile:
        for recipe in re.findall(r"^([A-Za-z][\w-]*)\s*[^\n=]*:(?!=)", _read_text(justfile), re.MULTILINE):
            role = _role_for(recipe)
            if role:
                _add(profile["commands"], role, f"just {recipe}", "justfile")


def detect_layout(root: Path, profile: dict) -> None:
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if child.name in SKIP_DIRS or child.name.startswith("."):
            if child.name in GENERATED_DIRS:
                profile["do_not_edit"].append(child.name + "/")
            continue
        if child.is_dir():
            if child.name in GENERATED_DIRS:
                profile["do_not_edit"].append(child.name + "/")
            else:
                profile["top_level_dirs"].append(child.name + "/")
    for secret in (".env", ".env.local", ".env.production"):
        if (root / secret).exists():
            profile["do_not_edit"].append(secret)

    workflows = root / ".github" / "workflows"
    if workflows.is_dir():
        profile["ci"].extend(sorted(f".github/workflows/{p.name}" for p in workflows.glob("*.y*ml")))
    for ci in (".gitlab-ci.yml", ".circleci/config.yml", "azure-pipelines.yml", "Jenkinsfile"):
        if (root / ci).exists():
            profile["ci"].append(ci)

    for rel in AGENT_CONFIGS:
        path = root / rel
        if path.exists():
            entry = {"path": rel, "kind": "dir" if path.is_dir() else "file"}
            if path.is_file():
                entry["lines"] = len(_read_text(path).splitlines())
            elif rel == ".claude/skills":
                entry["skills"] = sorted(p.parent.name for p in path.glob("*/SKILL.md"))
            profile["existing_agent_config"].append(entry)


def detect(root: Path) -> dict:
    profile: dict = {
        "root": str(root),
        "languages": [],
        "package_managers": [],
        "monorepo": False,
        "commands": [],
        "top_level_dirs": [],
        "do_not_edit": [],
        "ci": [],
        "existing_agent_config": [],
    }
    detect_node(root, profile)
    detect_python(root, profile)
    detect_other(root, profile)
    detect_task_runners(root, profile)
    detect_layout(root, profile)
    profile["languages"] = list(dict.fromkeys(profile["languages"]))
    profile["package_managers"] = list(dict.fromkeys(profile["package_managers"]))
    return profile


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"not a directory: {root}"}))
        return 1
    print(json.dumps(detect(root), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
