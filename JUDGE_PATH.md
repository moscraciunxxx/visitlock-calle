# JUDGE_PATH — VisitLock (CALL-E Devpost #30579)

Contest: https://call-e.devpost.com/ (id 30579)
Live door: public static HUD docs/index.html (GitHub Pages), not localhost.

## Gate A — Specific user + phone-work problem (~30s)
| Item | Answer |
|------|--------|
| Product | **VisitLock** |
| Tagline | Confirm research visits by phone — structured RSVPs, not voicemail limbo. |
| Specific user | Clinical/research coordinator chasing study visit confirmations |
| Phone-work problem | Missed/unclear visit confirmations cause no-shows and wasted slots |
| Number on first screen | confirmed / called, confirmation_rate %, reschedule_count |
| Fixture (never all zeros) | **3 / 5**, **60.0%**, **1** reschedule |
| MATLAB stamps | confirmation_rate + no_show_risk in artifacts/matlab/ |

Diff vs appointment-confirm: batch research-visit CSV, idempotent dial ledger, confirmation_rate HUD, research-visit consent language.

## Gate B — Ten-second try
Primary public door: docs/index.html with non-zero fixture numbers.
Secondary: python -m visitlock demo for local HUD only (not live door).

## Gate C — Public try-it (NOT localhost-only)

| Deliverable | Path | Role |
|-------------|------|------|
| Static HUD | docs/index.html | Live door |
| Board JSON | docs/board.json | Fixture + MATLAB stamps |
| Public HUD | docs/index.html | Board source of truth (twin still deferred) |
| MATLAB numbers | artifacts/matlab/ | confirmation_rate + no_show_risk |

Do not make .slx or Blender reel the live door. VoiceBank is local-only (demo/VOICEBANK.md).

## Technical proof

- calle-ai CalleClient.calls.create_and_wait when key set; fixture mode otherwise
- Schemas: visit_status yes|no|reschedule|no_answer|unknown, preferred_slot, notes
- CLI: demo | run --csv | serve; python -m unittest
- contribution/skills/visitlock + contribution/apps/python/visitlock

## Live CALL-E

Set CALLE_API_KEY and CALLE_BASE_URL to https://api.heycall-e.com then run with --live on authorized CSV only.
