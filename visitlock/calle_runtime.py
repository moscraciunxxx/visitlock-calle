"""CALL-E live runtime vs fixture mode."""

from __future__ import annotations

import os
from typing import Any

from visitlock.schema import RECIPIENT_RESULT_SCHEMA, RESULT_SCHEMA, validate_recipient_result


CONSENT_PREAMBLE = (
    "This is an automated research-visit confirmation call for a clinical research "
    "study. Participation is voluntary. You may decline, ask questions, or request "
    "a callback from the study coordinator. This call is not emergency care and is "
    "not affiliated with any hospital brand."
)


def build_task(participant: dict[str, str]) -> str:
    """Build CALL-E task text with explicit research-visit consent language."""
    name = participant.get("name", "participant")
    visit_dt = participant.get("visit_datetime", "the scheduled time")
    visit_type = participant.get("visit_type", "research visit")
    site = participant.get("site_label", "the LA clinic site")
    return (
        f"{CONSENT_PREAMBLE} "
        f"Call {name} and confirm whether they can attend their {visit_type} "
        f"on {visit_dt} at {site}. "
        "Ask clearly: can they confirm (yes), decline (no), or need to reschedule? "
        "If reschedule, capture a preferred slot. "
        "Record visit_status, preferred_slot, and brief notes. "
        "Be polite, concise, and stop if they withdraw consent to continue."
    )


def calle_available() -> bool:
    return bool(os.environ.get("CALLE_API_KEY", "").strip())


def create_and_wait_live(participant: dict[str, str]) -> dict[str, Any]:
    """Place one live CALL-E call and return validated recipient structured result."""
    from calle import CalleClient  # type: ignore

    api_key = os.environ["CALLE_API_KEY"]
    base_url = os.environ.get("CALLE_BASE_URL", "https://api.heycall-e.com")
    phone = participant["phone"]
    task = build_task(participant)

    client = CalleClient(api_key=api_key, base_url=base_url)
    try:
        call = client.calls.create_and_wait(
            task=task,
            recipients=[
                {
                    "phones": [phone],
                    "region": participant.get("region", "US"),
                    "locale": participant.get("locale", "en-US"),
                }
            ],
            result_schema=RESULT_SCHEMA,
            recipient_result_schema=RECIPIENT_RESULT_SCHEMA,
            metadata={
                "workflow": "visitlock",
                "participant_id": participant["participant_id"],
                "visit_datetime": participant["visit_datetime"],
            },
            idempotency_key=(
                f"visitlock_{participant['participant_id']}_"
                f"{participant['visit_datetime'].replace(' ', '_')}"
            ),
        )
    finally:
        client.close()

    recipients = call.get("recipients") or []
    if recipients and isinstance(recipients[0], dict):
        raw = recipients[0].get("structured_result") or {}
    else:
        raw = call.get("structured_result") or {}
    validated = validate_recipient_result(raw if isinstance(raw, dict) else {})
    return {
        "result": validated,
        "call_id": call.get("id") or call.get("call_id"),
        "status": call.get("status", "completed"),
        "mode": "live",
    }
