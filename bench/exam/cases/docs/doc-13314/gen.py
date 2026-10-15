#!/usr/bin/env python3
"""Generates doc-13314 (en, data handbook: application-log retention, old 2024 table vs 2026 revision notice)."""
import random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, offsets
from _doc import make_doc

CANARY = "EXAM-CANARY-d20f6b83"
rng = random.Random(13314)
OLD = ["## Data retention schedule (edition 2024)", "", "Effective date: 2024-11-01", "",
       "Unless a legal hold applies, the following retention periods are enforced by the nightly cleanup job:", "",
       "| Data class | Retention |", "|---|---|",
       "| Application logs | 90 days |", "| Audit logs | 365 days |", "| Database backups | 35 days |", "| Support attachments | 180 days |", "",
       "Retention periods are measured from the day the record was written."]
NEW = ["## Revision notice: retention schedule", "", "Effective date: 2026-05-15", "",
       "Following the storage cost review, the Data Council changed the schedule. This notice replaces edition 2024 for every class it lists; classes it does not list keep the old values.", "",
       "| Data class | Retention |", "|---|---|",
       "| Application logs | 45 days |", "| Support attachments | 120 days |", "",
       "Audit logs (365 days) and database backups (35 days) are unchanged."]
text = make_doc(rng, "en", "Platform Operations Handbook", 80, {28: OLD, 70: NEW})
size = check_size(text, 30_000, 60_000)
o_old, o_new = offsets(text, "Effective date: 2024-11-01")[0], offsets(text, "Effective date: 2026-05-15")[0]
assert o_new >= 40_000 and o_old < o_new
prompt = "How many days do we keep application logs before they get deleted? It's somewhere in data-handbook.md. I just need the number we go by now."
expect = {"expected_number": 45, "tolerance": 0.001, "expected_number_in_text": True}
finish(HERE, "doc-13314", CANARY, "docs", "policy_lookup", ["TR-LONG", "TR-SUPERSEDE"],
       {"TR-LONG": 90, "TR-SUPERSEDE": 90}, "L2", {"data-handbook.md": text}, prompt, expect,
       "Find the log retention period in a 50KB handbook where a later notice replaces the old schedule.",
       '''import re as _re
doc = case["files"]["data-handbook.md"]
assert doc.startswith("# Platform Operations Handbook")
best = None
for sec in doc.split("\\n## "):
    d = _re.search(r"Effective date: (\\d{4}-\\d{2}-\\d{2})", sec)
    v = _re.search(r"\\| Application logs \\| (\\d+) days \\|", sec)
    if d and v and (best is None or d.group(1) > best[0]):
        best = (d.group(1), int(v.group(1)))
print(json.dumps({"expected": best[1]}))''',
       '''## Traps
- TR-LONG: handbook is %d bytes (the whole file fits in a 64KB read per the spec size range); the 2024 schedule sits at byte %d and the notice at byte %d.
- TR-SUPERSEDE: edition 2024 says application logs 90 days; the notice effective 2026-05-15 (dates read from the text) says 45 days and replaces the schedule. Audit logs (365) and backups (35) are other numbers in both sections.
## Reference solution
1. search_text "Application logs"; 2. read both hits, choose the later effective date: 45.
## Why the answer is unique
The notice states it replaces edition 2024 for the classes it lists, and application logs are listed. 90 is the retired value.''' % (size, o_old, o_new), axes=["LNG", "VER"])
print("ok", size, o_old, o_new)
