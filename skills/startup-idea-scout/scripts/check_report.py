#!/usr/bin/env python3
"""Check the structure and traceability of a Startup Idea Scout report.

Why a script instead of eyeballing it:
counting sections, adding up scores, checking that every [S3] exists, and
checking that every link made it into Sources are deterministic, repetitive,
easy-to-miss chores. Give them to code, not to reasoning.

The script only flags problems:
  ERROR  structure or traceability is broken; must be fixed; exit code 1
  WARN   needs your judgment (e.g. a percentage with no source mark); exit code unaffected

Usage:
    python3 scripts/check_report.py "<report.md>"
Exit codes: 0 pass / 1 has ERRORs / 2 usage or file error
Standard library only; Python 3.8+.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = ["## 0.", "## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## Sources"]
REQUIRED_FIELDS = ["One-liner", "Company shape", "Who pays", "Business model", "Market size",
                   "Pain evidence", "Why now", "Competitors", "Platform risk", "Company test",
                   "Your edge", "First validation", "3 interview questions",
                   "Kill criteria", "Score"]
SCORE_KEYS = ["pain", "why now", "market", "moat", "competition", "edge", "validation"]
COMPANY_TESTS = ["buyer", "size", "moat", "platform"]
MAX_SCORE = 35
REPORT_THRESHOLD = 25
URL = re.compile(r"https?://[A-Za-z0-9\-._~:/?#@!$&'*+,;=%]+")
SIG_REF = re.compile(r"\[S(\d+)\]")
SIG_ROW = re.compile(r"^\|\s*S(\d+)\s*\|(.*)$", re.M)
IDEA_HEAD = re.compile(r"^### Idea\s*(\d+):(.*)$", re.M)
TOTAL = re.compile(r"score\s*(\d+)\s*/\s*35", re.I)
NUMERIC_CLAIM = re.compile(
    r"\d+(?:\.\d+)?\s*%|\$\s?\d|\d+(?:\.\d+)?\s*(?:[MBK]\b|million|billion|yen|USD|JPY)", re.I)
SOURCE_MARK = re.compile(r"https?://|\[S\d+\]|self-reported|unverified|speculation|estimate|source", re.I)

errors: list[str] = []
warns: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warns.append(msg)


def section(text: str, start: str) -> str:
    """Return the text from a level-2 heading up to the next level-2 heading."""
    i = text.find(start)
    if i < 0:
        return ""
    j = text.find("\n## ", i + len(start))
    return text[i: j if j >= 0 else len(text)]


def norm_url(u: str) -> str:
    return u.rstrip(".,;:").rstrip("/")


def field_line(block: str, field: str) -> str:
    return next((ln for ln in block.splitlines() if f"**{field}**" in ln), "")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"✗ Cannot read file: {path}")
        return 2
    text = path.read_text(encoding="utf-8")

    # 1. Frontmatter
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm:
        err("Missing frontmatter")
    else:
        for key in ("date", "type", "theme", "budget"):
            if not re.search(rf"^{key}:", fm.group(1), re.M):
                err(f"Frontmatter is missing `{key}`")

    # 2. Required sections
    for s in REQUIRED_SECTIONS:
        if s not in text:
            err(f"Missing section \"{s}\"")

    # 3. Signal ledger
    ledger = section(text, "## 1.")
    signals: dict[str, str] = {}
    for num, rest in SIG_ROW.findall(ledger):
        signals[num] = rest.lower()
        if not URL.search(rest):
            err(f"Signal S{num} has no source link")
    if not signals:
        err("The signal ledger has no S1, S2… rows")
    retracted = {n for n, rest in signals.items() if "retracted" in rest}
    pain = [n for n, rest in signals.items() if "pain" in rest and n not in retracted]
    dev_hosts = ("news.ycombinator.com", "github.com", "hn.algolia.com")
    dev_pain = [n for n in pain if any(h in signals[n] for h in dev_hosts)]
    if pain and len(dev_pain) * 2 > len(pain):
        warn(f"{len(dev_pain)} of {len(pain)} pain signals come from Hacker News/GitHub; "
             "at least half should come from industry sources (filings, regulation, job postings, forums, reviews)")
    if signals and len(pain) < 6:
        warn(f"Only {len(pain)} valid pain signals (checkpoint A needs ≥ 6); "
             "the bottom line should say so if signal is insufficient")

    # 4. Ideas
    ideas_part = section(text, "## 2.")
    heads = list(IDEA_HEAD.finditer(ideas_part))
    insufficient = "insufficient signal" in section(text, "## 0.").lower()
    if not heads and not insufficient:
        err("No \"### Idea N: …\" headings under \"## 2.\"")
    if len(heads) > 5:
        err(f"{len(heads)} ideas; the maximum is 5")
    weak = 0
    for k, h in enumerate(heads):
        end = heads[k + 1].start() if k + 1 < len(heads) else len(ideas_part)
        block = ideas_part[h.start(): end]
        name = f"Idea {h.group(1)}"
        for f in REQUIRED_FIELDS:
            if f"**{f}**" not in block:
                err(f"{name} is missing field \"{f}\"")

        for r in sorted(set(SIG_REF.findall(block)), key=int):
            if r not in signals:
                err(f"{name} cites signal S{r}, which does not exist")
            elif r in retracted:
                err(f"{name} cites retracted signal S{r}; re-evaluate this idea")
        for field, kind in (("Pain evidence", "pain"), ("Why now", "capability")):
            line = field_line(block, field)
            ok = [r for r in SIG_REF.findall(line)
                  if r in signals and r not in retracted and kind in signals[r]]
            if not ok and not URL.search(line):
                err(f"{name}: \"{field}\" cites no valid {kind} signal or link")

        comp = field_line(block, "Competitors")
        if comp and not URL.search(comp):
            err(f"{name}: \"Competitors\" has no link (checkpoint B)")
        if "Pass criteria" not in block:
            err(f"{name}: the first validation has no \"Pass criteria\"")

        ct = field_line(block, "Company test").lower()
        for test in COMPANY_TESTS:
            m = re.search(rf"{test}\s*(pass|fail)", ct)
            if not m:
                err(f"{name}: company test is missing \"{test} pass/fail\"")
            elif m.group(1) == "fail":
                err(f"{name}: failed the \"{test}\" company test; it belongs under Killed candidates")
        ms = field_line(block, "Market size")
        if ms and not re.search(r"\d", ms):
            err(f"{name}: \"Market size\" has no numbers")
        if ms and not (URL.search(ms) or re.search(r"estimate|\[S\d+\]", ms, re.I)):
            err(f"{name}: \"Market size\" inputs are neither linked nor marked \"estimate\" (checkpoint B)")

        score_line = field_line(block, "Score")
        scores = []
        for key in SCORE_KEYS:
            m = re.search(rf"{re.escape(key)}\s*(\d)", score_line, re.I)
            if not m:
                err(f"{name}: score is missing \"{key}\"")
            else:
                v = int(m.group(1))
                if not 1 <= v <= 5:
                    err(f"{name}: \"{key}\" = {v}, outside 1–5")
                scores.append(v)
        t = TOTAL.search(h.group(0))
        if not t:
            err(f"{name}: heading has no \"score xx/35\"")
        elif len(scores) == len(SCORE_KEYS) and sum(scores) != int(t.group(1)):
            err(f"{name}: heading says {t.group(1)}, dimensions add up to {sum(scores)}")
        if t and int(t.group(1)) < REPORT_THRESHOLD:
            if "weak" not in h.group(0).lower():
                err(f"{name} scores below {REPORT_THRESHOLD}; mark it \"weak\" in the heading")
            weak += 1
    if weak > 1:
        err(f"{weak} ideas score below {REPORT_THRESHOLD}; keep at most one")
    if heads and len(heads) < 3 and "insufficient signal" not in section(text, "## 0.").lower():
        warn("Fewer than 3 ideas, but the bottom line does not say \"insufficient signal\"")

    # 5. Killed candidates
    killed = [ln for ln in section(text, "## 3.").splitlines() if ln.lstrip().startswith("- ")]
    if len(killed) < 3:
        err(f"\"Killed candidates\" has {len(killed)} entries; at least 3 are required")

    # 6. Every link is listed in Sources
    src = section(text, "## Sources")
    body = text.replace(src, "")
    src_urls = {norm_url(u) for u in URL.findall(src)}
    for u in sorted({norm_url(u) for u in URL.findall(body)}):
        if u not in src_urls:
            err(f"Link used in the body is missing from Sources: {u}")

    # 7. Numeric claims need a source mark (needs human judgment)
    for i, ln in enumerate(body.splitlines(), 1):
        if ln.startswith("|") and SIG_ROW.match(ln):
            continue
        if "Pass criteria" in ln:
            continue  # experiment targets, not factual claims
        if NUMERIC_CLAIM.search(ln) and not SOURCE_MARK.search(ln):
            warn(f"Line {i} has a number but no source mark: {ln.strip()[:70]}")

    for m in errors:
        print(f"ERROR  {m}")
    for m in warns:
        print(f"WARN   {m}")
    print(f"\n{len(errors)} ERROR(s), {len(warns)} WARN(s) | "
          f"{len(signals)} signals ({len(retracted)} retracted) | {len(heads)} ideas")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
