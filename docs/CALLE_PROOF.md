# CALL-E live proof — VisitLock

**Date:** 2026-09-05 (PT) / 2026-09-06 UTC  
**Project:** VisitLock (`calle-ai` SDK → `https://api.heycall-e.com`)

## What was proven

| Check | Result |
|-------|--------|
| `.env` present with `CALLE_API_KEY` | Yes (key not committed; not printed) |
| `POST /v1/calls` create | **HTTP 201** |
| Call object returned | `call_I7BcQGz0Ne_tVZbHRqfnHA` |
| Initial status | `queued` |
| Idempotent replay (same `Idempotency-Key`) | **HTTP 201**, same `call_id` |
| Live structured confirm (`create_and_wait`) | **Not run** |

## Why not a live structured confirm clip

Only fiction/test NANP **555** recipients were available (SDK example `+14155550100`, sample CSV `+15550100xxx`). There was **no authorized real-person phone** for a short successful structured RSVP.

Per safety policy: prove API create when a live dial would hit a non-test number without a clear fixture recipient. Here the recipient *is* a fiction 555 number, but waiting for a completed structured result / audio clip would still be a hung or empty dial — not a meaningful 10–15s confirm proof.

**Honest scope:** live **API create (201)** + GET echo, not a completed live conversation with `visit_status` filled.

## Evidence (local, gitignored)

Redacted JSON (phones masked as `+***0100`; no API key):

- `demo/calle_proof/create_proof.json`

Fields of note:

- `http_status_exact`: `201`
- `live_structured_confirm`: `false`
- `call_create_redacted.id` / `status`
- `recipient_phone_masked`: `+***0100`
- VisitLock `result_schema` + `recipient_result_schema` accepted on create
- Consent-bearing task text from `visitlock.calle_runtime.build_task`

## Clip

**No screen/audio clip** was captured. A clip would only be meaningful after a completed live confirm to an authorized test recipient.

## How to reproduce (authorized test number only)

```bash
# never commit .env
export CALLE_API_KEY=…   # from local .env
export CALLE_BASE_URL=https://api.heycall-e.com

# API create proof only (fiction 555) — what this doc covers
# or, with an authorized E.164 you own/control:
python -m visitlock run --csv path/to/authorized_one_row.csv --live
```

Do **not** point `--live` at the checked-in sample CSV in production workflows expecting real answers; those rows are fiction 555 placeholders for fixture/HUD demos.

## Not committed

- `.env` / API key
- Full phone numbers
- `demo/calle_proof/*` (gitignored)
