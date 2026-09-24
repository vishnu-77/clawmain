import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

DETECT = Path(__file__).resolve().parents[1] / "plugins/groundwork/skills/init/scripts/detect.py"
spec = importlib.util.spec_from_file_location("detect", DETECT)
detect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detect)


def make_repo(files: dict) -> Path:
    root = Path(tempfile.mkdtemp())
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def cmds(profile: dict) -> set:
    return {c["cmd"] for c in profile["commands"]}


class DetectTest(unittest.TestCase):
    def test_pnpm_typescript_monorepo(self):
        root = make_repo({
            "package.json": json.dumps({"scripts": {"test": "vitest", "lint": "eslint .", "build": "tsc"}}),
            "pnpm-lock.yaml": "",
            "pnpm-workspace.yaml": "packages: []",
            "tsconfig.json": "{}",
            "dist/index.js": "",
        })
        profile = detect.detect(root)
        self.assertEqual(profile["languages"], ["typescript"])
        self.assertEqual(profile["package_managers"], ["pnpm"])
        self.assertTrue(profile["monorepo"])
        self.assertTrue({"pnpm test", "pnpm run lint", "pnpm run build"} <= cmds(profile))
        self.assertIn("dist/", profile["do_not_edit"])

    def test_uv_python_with_ruff(self):
        root = make_repo({
            "pyproject.toml": "[project]\nname='x'\n[tool.ruff]\n[tool.pytest.ini_options]\n",
            "uv.lock": "",
            "tests/test_x.py": "",
        })
        profile = detect.detect(root)
        self.assertEqual(profile["package_managers"], ["uv"])
        self.assertTrue({"uv sync", "uv run pytest", "uv run ruff check ."} <= cmds(profile))

    def test_makefile_and_existing_config(self):
        root = make_repo({
            "go.mod": "module x",
            "Makefile": "test:\n\tgo test ./...\nVAR := 1\nlint:\n\tgolangci-lint run\n",
            "CLAUDE.md": "a\nb\n",
            ".claude/skills/release/SKILL.md": "---\nname: release\n---\n",
            ".github/workflows/ci.yml": "on: push",
        })
        profile = detect.detect(root)
        self.assertTrue({"make test", "make lint", "go test ./..."} <= cmds(profile))
        self.assertNotIn("make VAR", cmds(profile))
        configs = {c["path"]: c for c in profile["existing_agent_config"]}
        self.assertEqual(configs["CLAUDE.md"]["lines"], 2)
        self.assertEqual(configs[".claude/skills"]["skills"], ["release"])
        self.assertEqual(profile["ci"], [".github/workflows/ci.yml"])

    def test_empty_repo(self):
        profile = detect.detect(make_repo({}))
        self.assertEqual(profile["languages"], [])
        self.assertEqual(profile["commands"], [])


if __name__ == "__main__":
    unittest.main()
