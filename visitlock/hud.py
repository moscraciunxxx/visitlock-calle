"""Local coordinator HUD server + static docs export."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from visitlock.fixture import FIXTURE_RESULTS, aggregate_metrics

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
DOCS_DIR = REPO_ROOT / "docs"
DEFAULT_BOARD = Path("visitlock_board.json")


def default_fixture_board() -> dict[str, Any]:
    """Board used when no board file exists yet (demo preload)."""
    results = []
    # Match sample CSV order / flavor
    sample = [
        ("P001", "Maya Chen", "2026-09-10 09:00 PT", "Screening visit", "West LA research suite"),
        ("P002", "Jordan Lee", "2026-09-10 10:30 PT", "Follow-up visit", "West LA research suite"),
        ("P003", "Samira Ortiz", "2026-09-10 13:00 PT", "Consent review", "Beverly-adjacent clinic annex"),
        ("P004", "Alex Kim", "2026-09-11 09:00 PT", "Labs draw", "West LA research suite"),
        ("P005", "Riley Brooks", "2026-09-12 08:00 PT", "Fasting labs", "West LA research suite"),
    ]
    for pid, name, vdt, vtype, site in sample:
        fr = FIXTURE_RESULTS[pid]
        results.append(
            {
                "participant_id": pid,
                "name": name,
                "phone_masked": "***0100",
                "visit_datetime": vdt,
                "visit_type": vtype,
                "site_label": site,
                "mode": "fixture",
                "call_id": f"fixture-{pid}",
                **fr,
            }
        )
    return {
        "product": "VisitLock",
        "tagline": "Confirm research visits by phone — structured RSVPs, not voicemail limbo.",
        "mode": "fixture",
        "metrics": aggregate_metrics(results),
        "results": results,
    }


def load_board(board_path: Path | str | None = None) -> dict[str, Any]:
    path = Path(board_path) if board_path else DEFAULT_BOARD
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default_fixture_board()


def render_html(board: dict[str, Any]) -> str:
    metrics = board.get("metrics") or {}
    confirmed = metrics.get("confirmed", 0)
    called = metrics.get("called", 0)
    rate = metrics.get("confirmation_rate", 0)
    reschedules = metrics.get("reschedule_count", 0)
    rows_html = []
    for r in board.get("results") or []:
        status = r.get("visit_status", "unknown")
        badge = {
            "yes": "ok",
            "no": "bad",
            "reschedule": "warn",
            "no_answer": "mute",
            "unknown": "mute",
        }.get(status, "mute")
        rows_html.append(
            "<tr>"
            f"<td>{_esc(r.get('participant_id',''))}</td>"
            f"<td>{_esc(r.get('name',''))}</td>"
            f"<td>{_esc(r.get('visit_datetime',''))}</td>"
            f"<td><span class='badge {badge}'>{_esc(status)}</span></td>"
            f"<td>{_esc(r.get('preferred_slot') or '—')}</td>"
            f"<td>{_esc(r.get('notes',''))}</td>"
            "</tr>"
        )
    table_body = "\n".join(rows_html) or "<tr><td colspan='6'>No results</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>VisitLock — Coordinator HUD</title>
<style>
:root {{
  --bg:#0b1220; --card:#121a2b; --text:#e8eefc; --muted:#9bb0d4;
  --ok:#3ddc97; --warn:#ffc857; --bad:#ff6b6b; --accent:#6ea8fe;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  background: radial-gradient(1200px 600px at 10% -10%, #1a2a4a 0%, var(--bg) 55%);
  color: var(--text); min-height:100vh;
}}
header {{ padding:28px 24px 8px; max-width:1100px; margin:0 auto; }}
h1 {{ margin:0 0 6px; font-size:1.75rem; letter-spacing:-0.02em; }}
.tag {{ color:#a9b7d6; margin:0; }}
.grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px;
  max-width:1100px; margin:18px auto; padding:0 24px; }}
.card {{ background:var(--card); border:1px solid #243049; border-radius:14px; padding:18px 16px; }}
.metric {{ font-size:2rem; font-weight:700; }}
.label {{ color:#9bb0d4; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.06em; }}
.panel {{ max-width:1100px; margin:8px auto 40px; padding:0 24px; }}
table {{ width:100%; border-collapse:collapse; background:var(--card);
  border:1px solid #243049; border-radius:14px; overflow:hidden; }}
th, td {{ text-align:left; padding:12px 12px; border-bottom:1px solid #1e2a40; font-size:0.95rem; }}
th {{ color:#9bb0d4; font-weight:600; background:#0f1728; }}
.badge {{ padding:3px 8px; border-radius:999px; font-size:0.78rem; font-weight:600; }}
.badge.ok {{ background:#163528; color:var(--ok); }}
.badge.warn {{ background:#3a2e14; color:var(--warn); }}
.badge.bad {{ background:#3a1717; color:var(--bad); }}
.badge.mute {{ background:#1c2436; color:#9bb0d4; }}
.foot {{ color:#7f92b5; font-size:0.85rem; margin-top:14px; }}
@media (max-width:800px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<header>
  <h1>VisitLock</h1>
  <p class="tag">{_esc(board.get('tagline',''))} · mode: <strong>{_esc(board.get('mode','fixture'))}</strong></p>
</header>
<section class="grid" aria-label="Key metrics">
  <div class="card"><div class="label">confirmed / called</div>
    <div class="metric" id="confirmed-called">{confirmed} / {called}</div></div>
  <div class="card"><div class="label">confirmation_rate %</div>
    <div class="metric" id="confirmation-rate">{rate}</div></div>
  <div class="card"><div class="label">reschedule_count</div>
    <div class="metric" id="reschedule-count">{reschedules}</div></div>
</section>
<section class="panel">
  <table>
    <thead><tr>
      <th>ID</th><th>Name</th><th>Visit</th><th>Status</th><th>Preferred slot</th><th>Notes</th>
    </tr></thead>
    <tbody>
{table_body}
    </tbody>
  </table>
  <p class="foot">Research-visit confirmations for coordinators. Demo uses fictional 555 numbers. Not affiliated with any hospital.</p>
</section>
<script id="board-data" type="application/json">{json.dumps(board)}</script>
</body>
</html>
"""


def _esc(value: Any) -> str:
    s = str(value)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def export_static_docs(board: dict[str, Any] | None = None, out_path: Path | None = None) -> Path:
    """Write Gate-C static HUD for GitHub Pages / Devpost try-it."""
    board = board or default_fixture_board()
    out = out_path or (DOCS_DIR / "index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(board), encoding="utf-8")
    # Also dump JSON sidecar for tests / judges
    (out.parent / "board.json").write_text(json.dumps(board, indent=2) + "\n", encoding="utf-8")
    return out


def serve_hud(host: str = "127.0.0.1", port: int = 8765, board_path: Path | str | None = None) -> None:
    board_holder: dict[str, Any] = {"board": load_board(board_path)}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path in ("/", "/index.html"):
                body = render_html(board_holder["board"]).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path == "/api/board":
                body = json.dumps(board_holder["board"]).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_error(404)

        def log_message(self, fmt: str, *args: Any) -> None:
            return

    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"VisitLock HUD → http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nHUD stopped.")
    finally:
        httpd.server_close()


def serve_hud_background(host: str = "127.0.0.1", port: int = 8765, board_path: Path | str | None = None):
    """Start HUD in a daemon thread (used by demo)."""
    t = threading.Thread(target=serve_hud, kwargs={"host": host, "port": port, "board_path": board_path}, daemon=True)
    t.start()
    return t
