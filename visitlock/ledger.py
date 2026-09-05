"""Idempotent batch ledger so re-runs do not double-dial participants."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class BatchLedger:
    """Tracks call attempts by participant_id + visit_datetime key."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._entries: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self._entries = data

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._entries, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def make_key(participant_id: str, visit_datetime: str) -> str:
        return f"{participant_id}::{visit_datetime}"

    def already_called(self, participant_id: str, visit_datetime: str) -> bool:
        key = self.make_key(participant_id, visit_datetime)
        entry = self._entries.get(key)
        return bool(entry and entry.get("status") in {"completed", "skipped_fixture"})

    def record(
        self,
        participant_id: str,
        visit_datetime: str,
        *,
        status: str,
        result: dict[str, Any] | None = None,
        call_id: str | None = None,
    ) -> None:
        key = self.make_key(participant_id, visit_datetime)
        self._entries[key] = {
            "participant_id": participant_id,
            "visit_datetime": visit_datetime,
            "status": status,
            "call_id": call_id,
            "result": result or {},
        }
        self.save()

    def get(self, participant_id: str, visit_datetime: str) -> dict[str, Any] | None:
        return self._entries.get(self.make_key(participant_id, visit_datetime))

    def all_entries(self) -> dict[str, dict[str, Any]]:
        return dict(self._entries)
