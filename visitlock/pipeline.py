"""Batch CSV pipeline: fixture or live CALL-E with idempotent ledger."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from visitlock.calle_runtime import calle_available, create_and_wait_live
from visitlock.fixture import aggregate_metrics, fixture_result_for
from visitlock.ledger import BatchLedger
from visitlock.schema import validate_recipient_result

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = PACKAGE_DIR / "data" / "sample_participants.csv"
DEFAULT_LEDGER = Path("visitlock_ledger.json")
DEFAULT_BOARD = Path("visitlock_board.json")


def load_participants(csv_path: Path | str) -> list[dict[str, str]]:
    path = Path(csv_path)
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = [dict(row) for row in reader]
    required = {"participant_id", "name", "phone", "visit_datetime"}
    for i, row in enumerate(rows):
        missing = required - set(row.keys())
        if missing:
            raise ValueError(f"CSV row {i} missing columns: {sorted(missing)}")
        for key in required:
            if not (row.get(key) or "").strip():
                raise ValueError(f"CSV row {i} empty required field: {key}")
    return rows


def run_batch(
    csv_path: Path | str | None = None,
    *,
    ledger_path: Path | str | None = None,
    board_path: Path | str | None = None,
    force_fixture: bool = False,
    force_live: bool = False,
) -> dict[str, Any]:
    """Run confirmation batch; skip ledger hits to avoid double-dial."""
    csv_path = Path(csv_path) if csv_path else DEFAULT_CSV
    ledger_path = Path(ledger_path) if ledger_path else DEFAULT_LEDGER
    board_path = Path(board_path) if board_path else DEFAULT_BOARD

    participants = load_participants(csv_path)
    ledger = BatchLedger(ledger_path)
    use_live = force_live or (calle_available() and not force_fixture)
    if force_live and not calle_available():
        raise RuntimeError("CALLE_API_KEY required for live mode")

    rows_out: list[dict[str, Any]] = []
    for p in participants:
        pid = p["participant_id"]
        vdt = p["visit_datetime"]
        if ledger.already_called(pid, vdt):
            prior = ledger.get(pid, vdt) or {}
            result = validate_recipient_result(prior.get("result") or fixture_result_for(pid))
            rows_out.append(
                {
                    "participant_id": pid,
                    "name": p["name"],
                    "phone_masked": _mask(p["phone"]),
                    "visit_datetime": vdt,
                    "visit_type": p.get("visit_type", ""),
                    "site_label": p.get("site_label", ""),
                    "mode": "ledger",
                    "call_id": prior.get("call_id"),
                    **result,
                }
            )
            continue

        if use_live:
            live = create_and_wait_live(p)
            result = live["result"]
            ledger.record(
                pid,
                vdt,
                status="completed",
                result=result,
                call_id=live.get("call_id"),
            )
            mode = "live"
            call_id = live.get("call_id")
        else:
            result = validate_recipient_result(fixture_result_for(pid))
            ledger.record(
                pid,
                vdt,
                status="skipped_fixture",
                result=result,
                call_id=f"fixture-{pid}",
            )
            mode = "fixture"
            call_id = f"fixture-{pid}"

        rows_out.append(
            {
                "participant_id": pid,
                "name": p["name"],
                "phone_masked": _mask(p["phone"]),
                "visit_datetime": vdt,
                "visit_type": p.get("visit_type", ""),
                "site_label": p.get("site_label", ""),
                "mode": mode,
                "call_id": call_id,
                **result,
            }
        )

    metrics = aggregate_metrics(rows_out)
    board = {
        "product": "VisitLock",
        "tagline": "Confirm research visits by phone — structured RSVPs, not voicemail limbo.",
        "mode": "live" if use_live else "fixture",
        "metrics": metrics,
        "results": rows_out,
    }
    board_path.write_text(json.dumps(board, indent=2) + "\n", encoding="utf-8")
    return board


def _mask(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 4:
        return "***"
    return f"+{digits[0]}***{digits[-4:]}" if phone.startswith("+") else f"***{digits[-4:]}"
