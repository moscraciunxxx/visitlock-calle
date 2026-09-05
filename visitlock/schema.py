"""Structured result schemas for CALL-E research-visit confirmation calls."""

from __future__ import annotations

from typing import Any

VISIT_STATUS_ENUM = ("yes", "no", "reschedule", "no_answer", "unknown")

RECIPIENT_RESULT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["visit_status", "preferred_slot", "notes"],
    "properties": {
        "visit_status": {
            "type": "string",
            "enum": list(VISIT_STATUS_ENUM),
            "description": "Participant response to the scheduled research visit.",
        },
        "preferred_slot": {
            "type": "string",
            "description": "Preferred reschedule slot if visit_status is reschedule; else empty.",
        },
        "notes": {
            "type": "string",
            "description": "Brief coordinator-facing notes from the call.",
        },
    },
    "additionalProperties": False,
}

RESULT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["completed_count", "confirmed_count", "reschedule_count"],
    "properties": {
        "completed_count": {"type": "integer"},
        "confirmed_count": {"type": "integer"},
        "reschedule_count": {"type": "integer"},
    },
    "additionalProperties": False,
}


def validate_recipient_result(result: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a per-recipient structured result."""
    if not isinstance(result, dict):
        raise ValueError("recipient result must be a dict")
    status = result.get("visit_status", "unknown")
    if status not in VISIT_STATUS_ENUM:
        raise ValueError(f"invalid visit_status: {status!r}")
    preferred = result.get("preferred_slot", "")
    notes = result.get("notes", "")
    if not isinstance(preferred, str) or not isinstance(notes, str):
        raise ValueError("preferred_slot and notes must be strings")
    return {
        "visit_status": status,
        "preferred_slot": preferred,
        "notes": notes,
    }
