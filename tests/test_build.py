import copy
import importlib.util
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1] / "tools/build.py"
spec = importlib.util.spec_from_file_location("build", BUILD)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

AGENT = {
    "name": "sample-agent",
    "description": "Does a thing. Use when a thing is needed.",
    "why": "sample lesson",
    "model": "haiku",
    "mode": "read-only",
    "loop_stage": "verify",
    "tools": ["Read", "Grep"],
    "mission": "Do the thing.",
    "steps": ["one", "two", "three"],
    "outputs": ["report"],
    "guardrails": ["be careful"],
}
DEPT = {"_src": "x.toml", "slug": "sample", "title": "Sample", "summary": "s",
        "recommend_when": "r", "color": "cyan"}


def dept_with(**overrides):
    agent = {**copy.deepcopy(AGENT), **overrides}
    return [{**DEPT, "agents": [agent]}]


class ValidateTest(unittest.TestCase):
    def test_valid_agent_passes(self):
        self.assertEqual(build.validate(dept_with()), [])

    def test_read_only_agent_cannot_write(self):
        errors = build.validate(dept_with(tools=["Read", "Edit"]))
        self.assertTrue(any("read-only agent must not have" in e for e in errors))

    def test_description_needs_trigger(self):
        errors = build.validate(dept_with(description="Does a thing."))
        self.assertTrue(any("Use when" in e for e in errors))

    def test_why_tag_length(self):
        errors = build.validate(dept_with(why="far too many words here"))
        self.assertTrue(any("why must be 2-3 words" in e for e in errors))

    def test_unknown_handoff(self):
        errors = build.validate(dept_with(handoffs=[{"to": "nobody", "when": "never"}]))
        self.assertTrue(any("unknown agent 'nobody'" in e for e in errors))


class RenderTest(unittest.TestCase):
    def test_agent_has_frontmatter_and_harness(self):
        dept = dept_with()[0]
        text = build.render_agent(dept, dept["agents"][0],
                                  "Budget {max_iterations} / {max_tokens}", {"sample-agent": "sample"})
        self.assertTrue(text.startswith("---\nname: sample-agent\n"))
        self.assertIn('description: "Does a thing. Use when a thing is needed."', text)
        self.assertIn("Budget 4 / 40000", text)
        self.assertIn("Read-only: do not modify files", text)


class CatalogTest(unittest.TestCase):
    def test_real_catalog_is_valid_and_built(self):
        departments = build.load_departments()
        self.assertEqual(build.validate(departments), [])
        outputs = build.build()
        stale = [p for p, t in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != t]
        self.assertEqual(stale, [], "run: python tools/build.py")


if __name__ == "__main__":
    unittest.main()
