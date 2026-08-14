import tempfile
import unittest
from pathlib import Path

from benchmark.benchmark_runner import (
    interleaved_schedule,
    snapshot_fingerprint,
    validate_snapshot,
)


class RunnerScheduleTests(unittest.TestCase):
    def test_schedule_alternates_first_label_by_trial(self):
        self.assertEqual(
            [
                ("clean", 1),
                ("spiked", 1),
                ("spiked", 2),
                ("clean", 2),
                ("clean", 3),
                ("spiked", 3),
            ],
            interleaved_schedule(3),
        )


class SnapshotGuardTests(unittest.TestCase):
    def _make_snapshot(self, root: Path, content: str = "console.log('ok');") -> Path:
        root.mkdir()
        (root / "index.js").write_text(content, encoding="utf-8")
        return root

    def test_rejects_snapshot_with_git_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = self._make_snapshot(Path(tmp) / "repo")
            (snapshot / ".git").mkdir()
            with self.assertRaisesRegex(ValueError, "con .git"):
                validate_snapshot(snapshot, "clean")

    def test_fingerprint_changes_when_source_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = self._make_snapshot(Path(tmp) / "repo")
            before = snapshot_fingerprint(snapshot)
            (snapshot / "index.js").write_text("console.log('changed');", encoding="utf-8")
            after = snapshot_fingerprint(snapshot)
            self.assertNotEqual(before, after)


if __name__ == "__main__":
    unittest.main()
