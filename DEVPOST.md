# Devpost field pack — VisitLock

Paste-ready narrative: **`docs/DEVPOST_STORY.md`** (Inspiration → What’s next).
Do **not** submit the Devpost software entry until video + final links are set.

## Project name

VisitLock

## Tagline

Confirm research visits by phone — structured RSVPs, not voicemail limbo.

## Built with

Python, CALL-E, calle-ai, JSON Schema, HTTP HUD, GitHub Pages, MATLAB, Blender, unittest, CLI

## CALL-E account email

Fill on the Devpost form only. Do not commit a personal address here (use a reserved fictional contact in public docs if a placeholder is required).

## Links

| Field | Value |
|-------|--------|
| Try it out | https://moscraciunxxx.github.io/visitlock-calle/ |
| GitHub repo | https://github.com/moscraciunxxx/visitlock-calle |
| Awesome PR | https://github.com/CALLE-AI/awesome-phone-call-agents/pull/314 |
| Thumbnail | docs/assets/hud-still.png (Blender Metal twin still) |

## Video

Pending upload. Local cut (gitignored / untracked): `demo/visitlock-demo.mp4`

Suggested YouTube title: `VisitLock — CALL-E research-visit confirmations (Devpost demo)`

Suggested description:
VisitLock batch-confirms research visit slots with CALL-E structured RSVPs. Public HUD: https://moscraciunxxx.github.io/visitlock-calle/ — confirmation_rate 60%, 3/5 confirmed, 1 reschedule, MATLAB no_show_risk 10.0.

## Setup reminders

- Static (no install): Pages HUD above — fixture, no `.env`.
- Local: `pip install -e . && python -m visitlock demo`
- Live: set `CALLE_API_KEY` + `CALLE_BASE_URL` in gitignored `.env`, then `python -m visitlock run --csv … --live`
