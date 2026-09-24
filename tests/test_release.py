import importlib.util
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bump = load("bump")
release_meta = load("release_meta")


class BumpTest(unittest.TestCase):
    def test_levels(self):
        self.assertEqual(bump.bumped("1.2.3", "patch"), "1.2.4")
        self.assertEqual(bump.bumped("1.2.3", "minor"), "1.3.0")
        self.assertEqual(bump.bumped("1.2.3", "major"), "2.0.0")
        self.assertEqual(bump.bumped("1.2.3-rc.1", "patch"), "1.2.4")


class ReleaseMetaTest(unittest.TestCase):
    def test_current_metadata_is_valid(self):
        self.assertEqual(release_meta.main(["release_meta.py"]), 0)

    def test_changelog_has_current_version(self):
        import json
        data = json.loads((TOOLS.parent / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertTrue(release_meta.changelog_section(data["metadata"]["version"]))


if __name__ == "__main__":
    unittest.main()
