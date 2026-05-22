"""Core engine for PARTNERMAP.

Reads partnership agreements written as small YAML files, hashes account
names so the raw customer list never leaves the file, computes account
overlap between partners, and surfaces renewal alerts.

The YAML subset supported here is intentionally tiny (keys, scalars, and
block/flow lists of scalars) so we can stay standard-library only and still
parse the kind of files this tool produces. No third-party deps.
"""
from __future__ import annotations

import datetime as _dt
import glob
import hashlib
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# --------------------------------------------------------------------------
# Minimal YAML parser (subset: mappings, scalars, block & flow lists)
# --------------------------------------------------------------------------

def _strip_comment(line: str) -> str:
    """Remove a trailing '# comment' that is not inside quotes."""
    out = []
    quote = None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out)


def _coerce(value: str) -> Any:
    v = value.strip()
    if v == "" or v in ("~", "null", "Null", "NULL"):
        return None
    if (v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'"):
        return v[1:-1]
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    # flow list: [a, b, c]
    if v[0] == "[" and v[-1] == "]":
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [_coerce(p.strip()) for p in _split_flow(inner)]
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _split_flow(inner: str) -> List[str]:
    parts, cur, quote = [], [], None
    for ch in inner:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            cur.append(ch)
        elif ch == ",":
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur))
    return parts


def parse_yaml(text: str) -> Dict[str, Any]:
    """Parse the supported YAML subset into a nested dict/list structure.

    Supports top-level mappings, nested mappings via indentation, block
    lists ('- item'), and flow lists ('[a, b]'). Sufficient for the
    partnership-agreement files this tool reads and writes.
    """
    raw_lines = text.splitlines()
    lines: List[Tuple[int, str]] = []
    for ln in raw_lines:
        stripped = _strip_comment(ln)
        if stripped.strip() == "":
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.strip()))

    pos = 0

    def parse_block(min_indent: int) -> Any:
        nonlocal pos
        # Decide list vs mapping by first line at this indent.
        if pos >= len(lines):
            return None
        indent, content = lines[pos]
        if content.startswith("- ") or content == "-":
            return parse_list(indent)
        return parse_map(indent)

    def parse_list(indent: int) -> List[Any]:
        nonlocal pos
        items: List[Any] = []
        while pos < len(lines):
            cur_indent, content = lines[pos]
            if cur_indent < indent or not (content.startswith("- ") or content == "-"):
                break
            item_body = content[1:].strip()
            pos += 1
            if item_body == "":
                items.append(parse_block(indent + 1))
            elif ":" in item_body and not item_body.startswith("["):
                # inline mapping start on the dash line
                key, _, val = item_body.partition(":")
                m: Dict[str, Any] = {}
                if val.strip() == "":
                    m[key.strip()] = parse_block(indent + 2)
                else:
                    m[key.strip()] = _coerce(val)
                # absorb following deeper mapping lines
                while pos < len(lines) and lines[pos][0] > indent and not (
                    lines[pos][1].startswith("- ") or lines[pos][1] == "-"
                ):
                    k2, _, v2 = lines[pos][1].partition(":")
                    pos += 1
                    if v2.strip() == "":
                        m[k2.strip()] = parse_block(indent + 2)
                    else:
                        m[k2.strip()] = _coerce(v2)
                items.append(m)
            else:
                items.append(_coerce(item_body))
        return items

    def parse_map(indent: int) -> Dict[str, Any]:
        nonlocal pos
        mapping: Dict[str, Any] = {}
        while pos < len(lines):
            cur_indent, content = lines[pos]
            if cur_indent < indent:
                break
            if content.startswith("- ") or content == "-":
                break
            key, sep, val = content.partition(":")
            if sep == "":
                # not a mapping line; stop
                break
            pos += 1
            key = key.strip()
            if val.strip() == "":
                # nested block follows if more-indented
                if pos < len(lines) and lines[pos][0] > indent:
                    mapping[key] = parse_block(lines[pos][0])
                else:
                    mapping[key] = None
            else:
                mapping[key] = _coerce(val)
        return mapping

    result = parse_block(0)
    return result if isinstance(result, dict) else {"_root": result}


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

def _normalize_account(name: str) -> str:
    """Normalize a company name for matching: lowercase, strip common
    suffixes/punctuation so 'Acme, Inc.' == 'acme inc' == 'ACME'."""
    n = name.strip().lower()
    for ch in ",.’'\"()":
        n = n.replace(ch, "")
    n = " ".join(n.split())
    suffixes = (" incorporated", " inc", " llc", " ltd", " corp",
                " corporation", " co", " company", " plc", " gmbh")
    changed = True
    while changed:
        changed = False
        for s in suffixes:
            if n.endswith(s):
                n = n[: -len(s)].strip()
                changed = True
    return n


def account_token(name: str) -> str:
    """Stable hashed token for an account name. The privacy primitive:
    two parties can compare tokens for overlap without revealing names."""
    norm = _normalize_account(name)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


@dataclass
class Partner:
    name: str
    tier: str = ""
    start_date: Optional[str] = None
    renewal_date: Optional[str] = None
    contact: Optional[str] = None
    accounts: List[str] = field(default_factory=list)
    source_file: Optional[str] = None

    @property
    def tokens(self) -> Dict[str, str]:
        """map token -> normalized account name (local view only)."""
        return {account_token(a): _normalize_account(a) for a in self.accounts}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "tier": self.tier,
            "start_date": self.start_date,
            "renewal_date": self.renewal_date,
            "contact": self.contact,
            "account_count": len(self.accounts),
            "source_file": self.source_file,
        }


@dataclass
class Overlap:
    partner_a: str
    partner_b: str
    shared: List[str]

    @property
    def count(self) -> int:
        return len(self.shared)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "partner_a": self.partner_a,
            "partner_b": self.partner_b,
            "shared_count": self.count,
            "shared_accounts": sorted(self.shared),
        }


@dataclass
class RenewalAlert:
    partner: str
    renewal_date: str
    days_until: int
    severity: str  # 'overdue' | 'due-soon' | 'upcoming'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "partner": self.partner,
            "renewal_date": self.renewal_date,
            "days_until": self.days_until,
            "severity": self.severity,
        }


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def _partner_from_dict(d: Dict[str, Any], source: Optional[str]) -> Partner:
    accounts = d.get("accounts") or []
    if not isinstance(accounts, list):
        accounts = [accounts]
    accounts = [str(a) for a in accounts if a is not None and str(a).strip()]
    return Partner(
        name=str(d.get("name") or d.get("partner") or "unnamed"),
        tier=str(d.get("tier") or ""),
        start_date=(str(d["start_date"]) if d.get("start_date") else None),
        renewal_date=(str(d["renewal_date"]) if d.get("renewal_date") else None),
        contact=(str(d["contact"]) if d.get("contact") else None),
        accounts=accounts,
        source_file=source,
    )


def load_partner_file(path: str) -> List[Partner]:
    """Load one or more Partner records from a single YAML file.

    Supports either a single partner mapping, or a top-level 'partners:'
    list of partner mappings.
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = parse_yaml(fh.read())
    partners: List[Partner] = []
    if isinstance(data, dict) and isinstance(data.get("partners"), list):
        for entry in data["partners"]:
            if isinstance(entry, dict):
                partners.append(_partner_from_dict(entry, path))
    elif isinstance(data, dict) and (data.get("name") or data.get("partner")):
        partners.append(_partner_from_dict(data, path))
    elif isinstance(data, dict) and isinstance(data.get("_root"), list):
        for entry in data["_root"]:
            if isinstance(entry, dict):
                partners.append(_partner_from_dict(entry, path))
    return partners


def load_partners(paths: List[str]) -> List[Partner]:
    """Load partners from a list of files and/or directories.

    Directories are scanned for *.yml and *.yaml files.
    """
    files: List[str] = []
    for p in paths:
        if os.path.isdir(p):
            for ext in ("*.yml", "*.yaml"):
                files.extend(sorted(glob.glob(os.path.join(p, "**", ext),
                                              recursive=True)))
        else:
            files.append(p)
    partners: List[Partner] = []
    for f in files:
        partners.extend(load_partner_file(f))
    return partners


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

def compute_overlaps(partners: List[Partner]) -> List[Overlap]:
    """Compute pairwise shared accounts via hashed tokens.

    Matching uses sha256 tokens, so the comparison would work even if
    each side only shared tokens (not raw names). We resolve tokens back
    to normalized names locally for the report.
    """
    overlaps: List[Overlap] = []
    n = len(partners)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = partners[i], partners[j]
            ta, tb = a.tokens, b.tokens
            shared_tokens = set(ta) & set(tb)
            if shared_tokens:
                shared_names = sorted({ta[t] for t in shared_tokens})
                overlaps.append(Overlap(a.name, b.name, shared_names))
    overlaps.sort(key=lambda o: o.count, reverse=True)
    return overlaps


def _parse_date(s: str) -> Optional[_dt.date]:
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return _dt.datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None


def renewal_alerts(
    partners: List[Partner],
    today: Optional[_dt.date] = None,
    window_days: int = 60,
) -> List[RenewalAlert]:
    """Surface renewals that are overdue or within `window_days`."""
    today = today or _dt.date.today()
    alerts: List[RenewalAlert] = []
    for p in partners:
        if not p.renewal_date:
            continue
        d = _parse_date(p.renewal_date)
        if d is None:
            continue
        days = (d - today).days
        if days < 0:
            sev = "overdue"
        elif days <= window_days:
            sev = "due-soon"
        else:
            continue
        alerts.append(RenewalAlert(p.name, p.renewal_date, days, sev))
    alerts.sort(key=lambda a: a.days_until)
    return alerts


def analyze(
    partners: List[Partner],
    today: Optional[_dt.date] = None,
    window_days: int = 60,
) -> Dict[str, Any]:
    """Full analysis bundle: partners, overlaps, renewal alerts, totals."""
    overlaps = compute_overlaps(partners)
    alerts = renewal_alerts(partners, today=today, window_days=window_days)
    all_tokens = set()
    for p in partners:
        all_tokens |= set(p.tokens)
    return {
        "partners": [p.to_dict() for p in partners],
        "overlaps": [o.to_dict() for o in overlaps],
        "renewal_alerts": [a.to_dict() for a in alerts],
        "summary": {
            "partner_count": len(partners),
            "unique_accounts": len(all_tokens),
            "overlap_pairs": len(overlaps),
            "shared_account_instances": sum(o.count for o in overlaps),
            "renewal_alert_count": len(alerts),
            "overdue_count": sum(1 for a in alerts if a.severity == "overdue"),
        },
    }
