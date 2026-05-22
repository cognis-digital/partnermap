"""Smoke tests for PARTNERMAP. Run with: pytest -q. No network."""
import datetime as dt
import json
import os
import subprocess
import sys

import partnermap
from partnermap import core

DEMO_DIR = os.path.join(os.path.dirname(__file__), "..", "demos", "01-basic")
DEMO_FILE = os.path.join(DEMO_DIR, "partners.yaml")
TODAY = dt.date(2026, 6, 8)


def test_exports():
    assert partnermap.TOOL_NAME == "partnermap"
    assert isinstance(partnermap.TOOL_VERSION, str)


def test_yaml_parse_and_load():
    partners = core.load_partner_file(DEMO_FILE)
    names = {p.name for p in partners}
    assert names == {"AcmeCloud", "DataForge", "NimbusCRM"}
    acme = next(p for p in partners if p.name == "AcmeCloud")
    assert acme.tier == "strategic"
    assert acme.renewal_date == "2026-07-01"
    assert len(acme.accounts) == 4
    # flow-list parsing on NimbusCRM
    nimbus = next(p for p in partners if p.name == "NimbusCRM")
    assert nimbus.accounts == ["Initech", "Pied Piper", "Stark Industries"]


def test_account_normalization_token():
    # 'Globex, Inc.' and 'globex' must collide
    assert core.account_token("Globex, Inc.") == core.account_token("globex")
    assert core.account_token("Acme") != core.account_token("Initech")


def test_overlap_detection():
    partners = core.load_partner_file(DEMO_FILE)
    overlaps = core.compute_overlaps(partners)
    pairs = {
        frozenset((o.partner_a, o.partner_b)): sorted(o.shared)
        for o in overlaps
    }
    af = frozenset(("AcmeCloud", "DataForge"))
    an = frozenset(("AcmeCloud", "NimbusCRM"))
    assert af in pairs
    # globex + initech shared (normalized)
    assert "initech" in pairs[af]
    assert "globex" in pairs[af]
    assert pairs[an] == ["initech"]


def test_renewal_alerts():
    partners = core.load_partner_file(DEMO_FILE)
    alerts = core.renewal_alerts(partners, today=TODAY, window_days=60)
    by_name = {a.partner: a for a in alerts}
    assert by_name["DataForge"].severity == "overdue"
    assert by_name["AcmeCloud"].severity == "due-soon"
    assert "NimbusCRM" not in by_name  # outside 60d window


def test_analyze_summary():
    partners = core.load_partner_file(DEMO_FILE)
    report = core.analyze(partners, today=TODAY, window_days=60)
    s = report["summary"]
    assert s["partner_count"] == 3
    assert s["overlap_pairs"] == 2
    assert s["renewal_alert_count"] == 2
    assert s["overdue_count"] == 1


def _run_cli(*args):
    cmd = [sys.executable, "-m", "partnermap", *args]
    root = os.path.join(os.path.dirname(__file__), "..")
    return subprocess.run(cmd, capture_output=True, text=True, cwd=root)


def test_cli_json_and_exit_codes():
    # clean run -> exit 0
    r = _run_cli("analyze", "demos/01-basic", "--today", "2026-06-08",
                 "--format", "json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["summary"]["partner_count"] == 3

    # fail-on overdue -> exit 1
    r2 = _run_cli("analyze", "demos/01-basic", "--today", "2026-06-08",
                  "--fail-on", "overdue")
    assert r2.returncode == 1


def test_cli_version():
    r = _run_cli("--version")
    assert r.returncode == 0
    assert "partnermap" in r.stdout
