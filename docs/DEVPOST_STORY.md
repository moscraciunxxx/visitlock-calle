# Devpost story — VisitLock (paste-ready)

Contest: CALL-E / Devpost. Software draft: https://devpost.com/software/visitlock (id 1368394).
**Do not submit from this file alone** — paste into Devpost when the video + final links are ready.

**Public try-it:** https://moscraciunxxx.github.io/visitlock-calle/  
**Repo:** https://github.com/moscraciunxxx/visitlock-calle  
**Awesome PR:** https://github.com/CALLE-AI/awesome-phone-call-agents/pull/333  
**Tagline:** Confirm research visits by phone — structured RSVPs, not voicemail limbo.  
**Built with:** Python, CALL-E (calle-ai), JSON Schema, static HUD / GitHub Pages, MATLAB, Blender, unittest, CLI

CALL-E account email for the Devpost form: fill on the site only — do not put a personal address in the public repo.

---

## Inspiration

Clinical and research coordinators spend a large share of the day chasing visit confirmations. A missed call or a vague voicemail becomes a no-show and a wasted slot on a protocol calendar. SMS blasts and one-at-a-time appointment tools help a little, but they do not give a batch confirmation rate a coordinator can act on before clinic day.

VisitLock started from that ops gap: treat research-visit confirmation as phone work with a measurable board, not as inbox archaeology.

## What it does

VisitLock batch-confirms study visit slots from a CSV. Each participant gets a phone confirmation (live CALL-E or offline fixture) with explicit research-visit consent language. The agent must return structured RSVP fields: `visit_status` (`yes` | `no` | `reschedule` | `no_answer` | `unknown`), `preferred_slot`, and `notes`.

An idempotent ledger keyed by `participant_id::visit_datetime` prevents double-dialing when a batch is re-run. The coordinator HUD shows confirmed/called, confirmation_rate %, and reschedule_count. MATLAB quotes confirmation_rate and a no_show_risk score onto the same board.

Judges (or anyone) can open the public fixture HUD with non-zero numbers — no API key and no localhost:

https://moscraciunxxx.github.io/visitlock-calle/

Fixture snapshot: **3 / 5** confirmed, **60.0%** confirmation rate, **1** reschedule, MATLAB **no_show_risk 10.0**.

## How we built it

- **Python CLI** (`python -m visitlock`) for demo, CSV run, serve, and docs export.
- **CALL-E** via `calle-ai` `CalleClient.calls.create_and_wait` when `CALLE_API_KEY` is present; otherwise a deterministic fixture that preserves the same schemas.
- **JSON Schema** on call results so RSVP status is machine-checkable, not free text.
- **Static `docs/index.html` + `docs/board.json`** published on GitHub Pages as the stranger-openable door.
- **MATLAB** script stamps metrics into `artifacts/matlab/` and the board JSON.
- Public **Pages HUD** is the board source of truth (Blender twin still deferred until product-quality).
- **Contribution pack** for the awesome list: skill + app pointer (PR #333).

## Challenges we ran into

Keeping the public story honest was harder than wiring the happy path. The live door had to work cold on Pages with fixture numbers baked in, while live dials stayed behind a gitignored `.env`. We also had to draw a clear line versus generic appointment-confirm tools: batch study visits, ledger, confirmation_rate HUD, and research-visit consent language. Matching MATLAB-quoted risk to what the HUD shows — and keeping the public board as the only source of truth — took more editing than expected.

## Accomplishments that we're proud of

- A stranger can open the Pages HUD and read real fixture metrics in under thirty seconds.
- Fixture and live paths share the same RSVP schema and board shape.
- MATLAB risk is visible next to confirmation rate, not buried in a notebook.
- Awesome-list skill/app PR opened with an upstream pointer to this repo.
- Sample phones stay in the fictional 555 range; no secrets in the tracked tree.

## What we learned

Phone agents for research ops need structured outputs more than clever dialogue. Coordinators care about confirmation_rate and who still needs a human callback. Shipping a static fixture door early forced the product story to stay readable without a key, and it made live CALL-E a deliberate second step instead of a demo blocker.

## What's next

- Upload and link the demo video on Devpost (local cut lives outside git).
- Tighten live-call safety: clearer destination checks and base-URL defaults before `--live`.
- Optional coordinator actions from the HUD (retry no_answer, accept reschedule slot).
- Broader fixture scenarios (multi-site, multi-day) once the core board stays stable.

---

## Optional short “Try it out” blurb (Devpost field)

Open https://moscraciunxxx.github.io/visitlock-calle/ — fixture mode, 3/5 confirmed, 60% rate, MATLAB no_show_risk 10.0. No API key. For live calls locally: `cp .env.example .env`, set `CALLE_API_KEY`, then `python -m visitlock run --csv … --live` on authorized numbers only.
