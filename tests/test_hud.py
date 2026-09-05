import json
import tempfile
import unittest
from pathlib import Path

from visitlock.hud import default_fixture_board, export_static_docs, load_board, render_html
from visitlock.pipeline import run_batch


class TestHud(unittest.TestCase):
    def test_default_board_metrics_nonzero(self):
        board = default_fixture_board()
        m = board["metrics"]
        self.assertEqual(m["confirmed"], 3)
        self.assertEqual(m["called"], 5)
        self.assertEqual(m["confirmation_rate"], 60.0)
        self.assertEqual(m["reschedule_count"], 1)

    def test_render_contains_numbers(self):
        html = render_html(default_fixture_board())
        self.assertIn("3 / 5", html)
        self.assertIn(">60.0<", html)
        self.assertIn(">1<", html)
        self.assertIn("confirmed / called", html)
        self.assertIn("confirmation_rate", html)
        self.assertIn("reschedule_count", html)

    def test_export_docs_and_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "index.html"
            board = default_fixture_board()
            export_static_docs(board, out_path=out)
            html = out.read_text(encoding="utf-8")
            self.assertIn("3 / 5", html)
            sidecar = Path(tmp) / "board.json"
            data = json.loads(sidecar.read_text())
            self.assertEqual(data["metrics"]["reschedule_count"], 1)

    def test_board_json_from_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            board_path = Path(tmp) / "board.json"
            run_batch(force_fixture=True, board_path=board_path, ledger_path=Path(tmp) / "l.json")
            loaded = load_board(board_path)
            self.assertEqual(loaded["metrics"]["called"], 5)


if __name__ == "__main__":
    unittest.main()
