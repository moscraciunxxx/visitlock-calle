# VisitLock (Python app pack)

Runnable batch research-visit confirmation app for CALL-E.

Upstream: https://github.com/moscraciunxxx/visitlock-calle

## Why this app (vs appointment-confirm)

- Batch CSV of research visit slots
- Idempotent dial ledger (no double-dial)
- confirmation_rate HUD + reschedule_count
- Research-visit consent language in the CALL-E task
- Static docs/index.html for Gate C / GitHub Pages

## Setup

Clone the upstream repo, then:

```bash
pip install -e .
python -m visitlock demo          # fixture + local HUD
python -m visitlock run --csv ... # fixture or live
```

Dry-run / no-call path is the default when CALLE_API_KEY is unset.

## Side effects

Live mode places outbound phone calls via CALL-E. Cancellation: stop the CLI; ledger prevents re-dial of completed keys. Use authorized numbers only.

## Tests

PYTHONPATH=. python -m unittest discover -s tests -v
