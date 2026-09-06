# VisitLock

**Confirm research visits by phone — structured RSVPs, not voicemail limbo.**

For a **clinical/research coordinator** who needs batch visit confirmations, not one-off appointment reminders.

> Not affiliated with any hospital. Sample data uses fictional 555 numbers and LA-adjacent clinic flavor only.

## 30-second map

| | |
|---|---|
| **Problem** | Missed / unclear visit confirmations → no-shows and wasted study slots |
| **Phone step** | CALL-E places (or fixtures) confirmation calls with research-visit consent language |
| **Board** | Structured `visit_status` → confirmed/called, confirmation_rate %, reschedule_count |
| **MATLAB risk** | Quotes `confirmation_rate` + `no_show_risk` onto the board |
| **Try it** | [Public fixture HUD](https://moscraciunxxx.github.io/visitlock-calle/) — no API key |

**Spine:** problem → phone confirm → rate on board → MATLAB risk → try fixture.

## Try the fixture (no key)

Open the GitHub Pages HUD cold:

**https://moscraciunxxx.github.io/visitlock-calle/**

You should see mode **fixture**, **3 / 5** confirmed, **60.0%** confirmation rate, **1** reschedule, MATLAB **no_show_risk 10.0**, plus the board-twin still. Numbers are baked into static HTML/JSON — no `.env`, no localhost, no live dials.

Local mirror of the same door: open `docs/index.html` or run `python -m visitlock demo`.

## How it uses CALL-E

When `CALLE_API_KEY` is set in a **gitignored** `.env`, VisitLock uses the `calle-ai` SDK (`CalleClient.calls.create_and_wait`) with `result_schema` / `recipient_result_schema` so each call returns structured RSVP fields:

`visit_status` ∈ `yes | no | reschedule | no_answer | unknown`, plus `preferred_slot` and `notes`.

Without a key, the same schemas are filled by a **deterministic fixture** pipeline (CI, Pages, Devpost try-it). Live dials need:

```bash
cp .env.example .env   # then set CALLE_API_KEY (never commit .env)
# CALLE_BASE_URL=https://api.heycall-e.com
python -m visitlock run --csv path/to/authorized.csv --live
```

Fixture path works with zero secrets. Live path is opt-in and only for authorized numbers.

## MATLAB risk quote

MATLAB (`matlab/visitlock_metrics.m`) stamps batch outcomes into `artifacts/matlab/` and the board:

- `confirmation_rate=60.0`
- `no_show_risk=10.0`
- confirmed=3 / called=5 / reschedule_count=1

The HUD surfaces the no-show risk next to the confirmation metrics.

## Board twin (honest)

`docs/assets/hud-still.png` is a **Blender Metal still** of the coordinator board — a visual twin for thumbnails/demo, **not** a second live door. The interactive try-it is the static Pages HUD above.

## Demo video

_Placeholder — link the YouTube upload here when ready._

Local cut (not in git): `demo/visitlock-demo.mp4`

## Awesome PR

Upstream skill/app pointer for CALL-E:

https://github.com/CALLE-AI/awesome-phone-call-agents/pull/314

Pack in this repo: `contribution/skills/visitlock/` and `contribution/apps/python/visitlock/`.

## Setup (local)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env   # optional; only needed for --live
```

| Command | Role |
|---------|------|
| `python -m visitlock demo` | Fixture batch + HUD numbers |
| `python -m visitlock run --csv path` | Fixture/run against CSV |
| `python -m visitlock run --csv path --live` | Live CALL-E (needs `CALLE_API_KEY`) |
| `python -m visitlock serve` | Local HUD server |
| `python -m visitlock export-docs` | Refresh `docs/` static export |
| `PYTHONPATH=. python -m unittest discover -s tests -v` | Tests |

## Diff vs appointment-confirm

Batch study-visit CSV, idempotent dial ledger (no double-dial on re-runs), confirmation_rate HUD, research-visit consent language — not single consumer appointment confirm.

## License

MIT
