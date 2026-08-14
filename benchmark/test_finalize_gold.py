import tempfile
import unittest
from pathlib import Path

from benchmark.finalize_gold import finalize


class FinalizeGoldTests(unittest.TestCase):
    def test_resolves_unique_file_and_function_scoped_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp)
            (snapshot / "core").mkdir()
            (snapshot / "core" / "sample.js").write_text(
                "const target = 1;\n"
                "async function first() {\n"
                "  const repeated = true;\n"
                "}\n"
                "async function second() {\n"
                "  const repeated = true;\n"
                "}\n",
                encoding="utf-8",
            )
            data = {
                "_meta": {"total_seeded": 2},
                "seeded": [
                    {
                        "id": "FILE",
                        "file": "core/sample.js",
                        "anchor_after": "const target = 1;",
                        "final_line": None,
                    },
                    {
                        "id": "FUNC",
                        "file": "core/sample.js",
                        "anchor_handler": "async function second",
                        "anchor_after": "const repeated = true;",
                        "final_line": None,
                    },
                ],
            }
            updated, resolved = finalize(snapshot, data)
            self.assertEqual({"FILE": 1, "FUNC": 6}, resolved)
            self.assertEqual(6, updated["seeded"][1]["final_line"])
            self.assertIsNone(data["seeded"][1]["final_line"])  # input not mutated

    def test_refuses_incomplete_gold(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Gold chua du"):
                finalize(Path(tmp), {"_meta": {"total_seeded": 2}, "seeded": []})


if __name__ == "__main__":
    unittest.main()
