# Devpost field pack — VisitLock

CALL-E account email placeholder: vcerv001@gold.ac.uk (correct if needed).

## Project name

VisitLock

## Tagline

Confirm research visits by phone — structured RSVPs, not voicemail limbo.

## Built with

Python, CALL-E, calle-ai, JSON Schema, HTTP HUD, GitHub Pages, MATLAB, Blender, unittest, CLI

## CALL-E account email

vcerv001@gold.ac.uk

## Description (paste)

### The problem

Clinical and research coordinators burn hours chasing visit confirmations. Missed calls and vague voicemails turn into no-shows and wasted study slots. Existing tools either blast SMS or confirm one appointment at a time — they do not give a batch confirmation rate a coordinator can act on.

### What it does

VisitLock batch-calls participants from a CSV of research visit slots using CALL-E. Each call uses explicit research-visit consent language and returns structured RSVP fields: visit_status (yes|no|reschedule|no_answer|unknown), preferred_slot, and notes. An idempotent ledger prevents double-dialing on re-runs. A coordinator HUD shows confirmed/called, confirmation_rate %, and reschedule_count. MATLAB quotes confirmation_rate and a no_show_risk score into the board. Judges open docs/index.html (GitHub Pages) with non-zero fixture numbers — no localhost required.

### How CALL-E enables it

CALL-E CalleClient.calls.create_and_wait places the outbound confirmation call and returns schema-constrained structured results. VisitLock supplies result_schema and recipient_result_schema so the agent must capture visit RSVP status. Without an API key, a deterministic fixture pipeline preserves the same schemas for CI and Devpost demos.

### Setup / try it

Static (no install): open docs/index.html (GitHub Pages).

Local: pip install -e . && python -m visitlock demo

Live: set CALLE_API_KEY and CALLE_BASE_URL, then python -m visitlock run --csv your.csv --live

## Try it out link guidance

Prefer GitHub Pages URL for docs/ once published. Fallback: docs/index.html in the browser.

## Thumbnail

docs/assets/hud-still.png (Blender Metal twin still)
