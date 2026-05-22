"""Command-line interface for PARTNERMAP.

Examples
--------
  # Analyze a directory of partnership YAML files (table output)
  python -m partnermap analyze demos/01-basic

  # JSON for piping into CI / jq
  python -m partnermap analyze demos/01-basic --format json

  # Only fail CI when a renewal is overdue
  python -m partnermap analyze demos/01-basic --fail-on overdue

Exit codes
----------
  0  clean
  1  findings present per --fail-on (overlap | renewal | overdue | any)
  2  usage / load error
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from typing import List, Optional

from . import TOOL_NAME, TOOL_VERSION
from .core import analyze, load_partners


def _print_table(report: dict) -> None:
    s = report["summary"]
    print("PARTNERMAP report")
    print("=" * 60)
    print(f"Partners        : {s['partner_count']}")
    print(f"Unique accounts : {s['unique_accounts']}")
    print(f"Overlap pairs   : {s['overlap_pairs']}")
    print(f"Renewal alerts  : {s['renewal_alert_count']} "
          f"({s['overdue_count']} overdue)")
    print()

    overlaps = report["overlaps"]
    print("Account overlaps")
    print("-" * 60)
    if not overlaps:
        print("  (none)")
    for o in overlaps:
        print(f"  {o['partner_a']} <> {o['partner_b']}: "
              f"{o['shared_count']} shared")
        for acct in o["shared_accounts"]:
            print(f"      - {acct}")
    print()

    alerts = report["renewal_alerts"]
    print("Renewal alerts")
    print("-" * 60)
    if not alerts:
        print("  (none)")
    for a in alerts:
        when = (f"{a['days_until']}d" if a["days_until"] >= 0
                else f"{-a['days_until']}d ago")
        print(f"  [{a['severity']:<8}] {a['partner']:<24} "
              f"{a['renewal_date']} ({when})")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description="Track partnership agreements as YAML and compute "
                    "account overlap + renewal alerts — no customer-list "
                    "upload, runs fully local.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  python -m partnermap analyze demos/01-basic "
               "--format json\n",
    )
    p.add_argument("--version", action="version",
                   version=f"{TOOL_NAME} {TOOL_VERSION}")
    sub = p.add_subparsers(dest="command")

    an = sub.add_parser(
        "analyze",
        help="Analyze partnership YAML files for overlap and renewals.",
        description="Load partner YAML files/dirs and report account "
                    "overlap and renewal alerts.",
    )
    an.add_argument("paths", nargs="+",
                    help="YAML files and/or directories of partner files.")
    an.add_argument("--format", choices=["table", "json"], default="table",
                    help="Output format (default: table).")
    an.add_argument("--window-days", type=int, default=60,
                    help="Days ahead to flag upcoming renewals (default 60).")
    an.add_argument("--today", default=None,
                    help="Override 'today' as YYYY-MM-DD (for tests/CI).")
    an.add_argument("--fail-on", choices=["none", "overlap", "renewal",
                                          "overdue", "any"], default="none",
                    help="Exit non-zero when these findings exist.")
    return p


def _should_fail(report: dict, fail_on: str) -> bool:
    s = report["summary"]
    if fail_on == "none":
        return False
    if fail_on == "overlap":
        return s["overlap_pairs"] > 0
    if fail_on == "renewal":
        return s["renewal_alert_count"] > 0
    if fail_on == "overdue":
        return s["overdue_count"] > 0
    if fail_on == "any":
        return s["overlap_pairs"] > 0 or s["renewal_alert_count"] > 0
    return False


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "analyze":
        parser.print_help()
        return 2

    today = None
    if args.today:
        try:
            today = _dt.datetime.strptime(args.today, "%Y-%m-%d").date()
        except ValueError:
            print(f"error: --today must be YYYY-MM-DD, got {args.today!r}",
                  file=sys.stderr)
            return 2

    try:
        partners = load_partners(args.paths)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not partners:
        print("error: no partner records found in given paths",
              file=sys.stderr)
        return 2

    report = analyze(partners, today=today, window_days=args.window_days)

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_table(report)

    return 1 if _should_fail(report, args.fail_on) else 0


if __name__ == "__main__":
    sys.exit(main())
