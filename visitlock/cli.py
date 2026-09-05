"""VisitLock CLI: demo | run --csv | serve."""

from __future__ import annotations

import argparse
import json
import sys
import time
import webbrowser
from pathlib import Path

from visitlock.hud import DEFAULT_BOARD, export_static_docs, load_board, serve_hud
from visitlock.pipeline import DEFAULT_CSV, run_batch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="visitlock",
        description="VisitLock — batch research-visit confirmations via CALL-E",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_demo = sub.add_parser("demo", help="Fixture batch + open local HUD (offline)")
    p_demo.add_argument("--no-browser", action="store_true")
    p_demo.add_argument("--port", type=int, default=8765)

    p_run = sub.add_parser("run", help="Run batch from CSV (fixture or live CALL-E)")
    p_run.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    p_run.add_argument("--ledger", type=Path, default=Path("visitlock_ledger.json"))
    p_run.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    p_run.add_argument("--fixture", action="store_true", help="Force fixture mode")
    p_run.add_argument("--live", action="store_true", help="Force live CALL-E (needs key)")

    p_serve = sub.add_parser("serve", help="Serve coordinator HUD")
    p_serve.add_argument("--port", type=int, default=8765)
    p_serve.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    p_serve.add_argument("--host", default="127.0.0.1")

    p_export = sub.add_parser("export-docs", help="Write docs/index.html static HUD")
    p_export.add_argument("--board", type=Path, default=None)

    args = parser.parse_args(argv)

    if args.command == "demo":
        board = run_batch(force_fixture=True, board_path=DEFAULT_BOARD)
        export_static_docs(board)
        url = f"http://127.0.0.1:{args.port}"
        print(json.dumps(board["metrics"], indent=2))
        print(f"Static HUD: docs/index.html")
        print(f"Local HUD:  {url}")
        if not args.no_browser:
            # Open after short delay so server is up
            def _open() -> None:
                time.sleep(0.4)
                webbrowser.open(url)

            import threading

            threading.Thread(target=_open, daemon=True).start()
        serve_hud(port=args.port, board_path=DEFAULT_BOARD)
        return 0

    if args.command == "run":
        board = run_batch(
            args.csv,
            ledger_path=args.ledger,
            board_path=args.board,
            force_fixture=args.fixture,
            force_live=args.live,
        )
        export_static_docs(board)
        print(json.dumps(board["metrics"], indent=2))
        print(f"Wrote {args.board} and docs/index.html")
        return 0

    if args.command == "serve":
        if not Path(args.board).exists():
            # Ensure non-empty demo board
            run_batch(force_fixture=True, board_path=args.board)
        serve_hud(host=args.host, port=args.port, board_path=args.board)
        return 0

    if args.command == "export-docs":
        board = load_board(args.board) if args.board else None
        if board is None:
            # Prefer regenerating from fixture pipeline for consistency
            board = run_batch(force_fixture=True)
        path = export_static_docs(board)
        print(f"Wrote {path}")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
