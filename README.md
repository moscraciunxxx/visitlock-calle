# VisitLock

**Confirm research visits by phone — structured RSVPs, not voicemail limbo.**

VisitLock helps a **clinical/research coordinator** batch-confirm study visit slots with CALL-E. Coordinators get structured visit_status (yes|no|reschedule|no_answer|unknown) plus a HUD: confirmed/called, confirmation_rate %, reschedule_count.

> Not affiliated with any hospital. Sample data uses fictional 555 numbers and LA-adjacent clinic flavor only.

**Judge live door:** docs/index.html (GitHub Pages) — not localhost. See JUDGE_PATH.md (CALL-E Devpost #30579).

## Problem

Missed or unclear visit confirmations cause no-shows and wasted research slots.

## What it does

1. Batch CSV of research/clinical study visit slots (5-sample included).
2. CALL-E call (or fixture) with explicit research-visit consent language.
3. Structured RSVP via result_schema / recipient_result_schema.
4. Idempotent batch ledger so re-runs do not double-dial.
5. Static docs/index.html for GitHub Pages / Devpost try-it.
6. MATLAB quotes confirmation_rate + no_show_risk into artifacts/matlab/ and stamps board JSON.
7. Blender Metal still: docs/assets/hud-still.png (not a Blender-only door).

Different from appointment-confirm: batch study visits, ledger, confirmation_rate HUD.

## How CALL-E is used

calle-ai SDK CalleClient.calls.create_and_wait when CALLE_API_KEY is set. Fixture mode otherwise.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
```

## Try it (Gate C first)

1. Open docs/index.html (or GitHub Pages) — 3/5, 60%, 1 reschedule, MATLAB no_show_risk.
2. Local: python -m visitlock demo

## CLI

- python -m visitlock demo
- python -m visitlock run --csv path
- python -m visitlock run --csv path --live
- python -m visitlock serve
- python -m visitlock export-docs

## Live CALL-E

Set CALLE_API_KEY and CALLE_BASE_URL=https://api.heycall-e.com then run --live on authorized CSV only.

## Tests

PYTHONPATH=. python -m unittest discover -s tests -v

## Awesome PR pack

contribution/skills/visitlock/ and contribution/apps/python/visitlock/

## License

MIT
