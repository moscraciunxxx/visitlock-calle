import json
import tempfile
import unittest
from pathlib import Path

from visitlock.fixture import FIXTURE_RESULTS, aggregate_metrics, fixture_result_for
from visitlock.ledger import BatchLedger
from visitlock.pipeline import DEFAULT_CSV, load_participants, run_batch


class TestFixturePipeline(unittest.TestCase):
    def test_fixture_non_zero_metrics(self):
        results = [fixture_result_for(pid) for pid in sorted(FIXTURE_RESULTS)]
        m = aggregate_metrics(results)
        self.assertEqual(m["called"], 5)
        self.assertEqual(m["confirmed"], 3)
        self.assertEqual(m["reschedule_count"], 1)
        self.assertEqual(m["confirmation_rate"], 60.0)
        self.assertNotEqual(m["confirmed"], 0)
        self.assertNotEqual(m["called"], 0)

    def test_sample_csv_five_rows(self):
        rows = load_participants(DEFAULT_CSV)
        self.assertEqual(len(rows), 5)
        for row in rows:
            self.assertTrue(row["phone"].startswith("+1555"))

    def test_run_batch_fixture_and_ledger_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "ledger.json"
            board_path = tmp_path / "board.json"
            board1 = run_batch(
                DEFAULT_CSV,
                ledger_path=ledger,
                board_path=board_path,
                force_fixture=True,
            )
            board2 = run_batch(
                DEFAULT_CSV,
                ledger_path=ledger,
                board_path=board_path,
                force_fixture=True,
            )
            self.assertEqual(board1["metrics"], board2["metrics"])
            # Second pass should all be ledger hits
            self.assertTrue(all(r["mode"] == "ledger" for r in board2["results"]))
            led = BatchLedger(ledger)
            self.assertEqual(len(led.all_entries()), 5)
            data = json.loads(board_path.read_text())
            self.assertEqual(data["metrics"]["confirmed"], 3)


if __name__ == "__main__":
    unittest.main()
