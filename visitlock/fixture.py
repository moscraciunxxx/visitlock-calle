"""Deterministic fixture results for offline demo / CI (no CALL-E key)."""

from __future__ import annotations

from typing import Any

# Deterministic map: participant_id -> structured recipient result.
# Non-zero HUD: 3 confirmed / 5 called, rate 60%, 1 reschedule.
FIXTURE_RESULTS: dict[str, dict[str, Any]] = {
    "P001": {
        "visit_status": "yes",
        "preferred_slot": "",
        "notes": "Confirmed Thursday 9:00 AM visit; parking validated.",
    },
    "P002": {
        "visit_status": "reschedule",
        "preferred_slot": "2026-09-11 14:00 PT",
        "notes": "Out of town Thu morning; prefers next Thu afternoon.",
    },
    "P003": {
        "visit_status": "yes",
        "preferred_slot": "",
        "notes": "Confirmed; will bring signed consent packet.",
    },
    "P004": {
        "visit_status": "no_answer",
        "preferred_slot": "",
        "notes": "Voicemail after 2 rings; left research-visit callback note.",
    },
    "P005": {
        "visit_status": "yes",
        "preferred_slot": "",
        "notes": "Confirmed Friday fasting labs window.",
    },
}


def fixture_result_for(participant_id: str) -> dict[str, Any]:
    """Return deterministic structured result for a participant."""
    if participant_id in FIXTURE_RESULTS:
        return dict(FIXTURE_RESULTS[participant_id])
    # Stable fallback for extra CSV rows
    return {
        "visit_status": "unknown",
        "preferred_slot": "",
        "notes": f"Fixture fallback for {participant_id}",
    }


def aggregate_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute HUD metrics from a list of recipient results."""
    called = len(results)
    confirmed = sum(1 for r in results if r.get("visit_status") == "yes")
    reschedule_count = sum(1 for r in results if r.get("visit_status") == "reschedule")
    confirmation_rate = round((confirmed / called) * 100, 1) if called else 0.0
    return {
        "confirmed": confirmed,
        "called": called,
        "confirmation_rate": confirmation_rate,
        "reschedule_count": reschedule_count,
    }
