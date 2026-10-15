#!/usr/bin/env python3
"""Generates doc-13318 (en, procurement handbook: team-lead approval limit, 2025 table vs 2026 amendment)."""
import random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, offsets
from _doc import make_doc

CANARY = "EXAM-CANARY-e83b5d17"
rng = random.Random(13318)
OLD = ["## Purchase approval limits (2025 rules)", "", "Valid from: 2025-06-01", "",
       "Purchases are approved by the lowest level whose limit covers the full amount of the order:", "",
       "| Approver | Limit per order (EUR) |", "|---|---|",
       "| Team lead | 500 |", "| Department head | 2000 |", "| Finance director | above 2000 |", "",
       "Orders must not be split to stay under a limit."]
NEW = ["## Amendment: purchase approval limits", "", "Valid from: 2026-07-01", "",
       "The board raised the limits to reflect inflation. This amendment replaces the 2025 limits for the two lowest levels; the rule against splitting orders is unchanged:", "",
       "| Approver | Limit per order (EUR) |", "|---|---|",
       "| Team lead | 900 |", "| Department head | 3000 |", "",
       "Orders above 3000 EUR still go to the finance director."]
text = make_doc(rng, "en", "Procurement and Spending Handbook", 78, {26: OLD, 68: NEW})
size = check_size(text, 30_000, 60_000)
o_old, o_new = offsets(text, "Valid from: 2025-06-01")[0], offsets(text, "Valid from: 2026-07-01")[0]
assert o_new >= 40_000 and o_old < o_new
prompt = "Our team wants to order some equipment next week. Up to what amount can a team lead approve a purchase on their own, per order? The rules are in spending-handbook.md. Just give me the euro figure."
expect = {"expected_number": 900, "tolerance": 0.001, "expected_number_in_text": True}
finish(HERE, "doc-13318", CANARY, "docs", "policy_lookup", ["TR-LONG", "TR-SUPERSEDE"],
       {"TR-LONG": 500, "TR-SUPERSEDE": 500}, "L2", {"spending-handbook.md": text}, prompt, expect,
       "Find the team-lead approval limit in a 50KB handbook where a later amendment raises the 2025 limit.",
       '''import re as _re
doc = case["files"]["spending-handbook.md"]
assert doc.startswith("# Procurement and Spending Handbook")
best = None
for sec in doc.split("\\n## "):
    d = _re.search(r"Valid from: (\\d{4}-\\d{2}-\\d{2})", sec)
    v = _re.search(r"\\| Team lead \\| (\\d+) \\|", sec)
    if d and v and (best is None or d.group(1) > best[0]):
        best = (d.group(1), int(v.group(1)))
print(json.dumps({"expected": best[1]}))''',
       '''## Traps
- TR-LONG: handbook is %d bytes (within 30-60KB, so one 64KB read holds it); 2025 table at byte %d, amendment at %d.
- TR-SUPERSEDE: the 2025 rules say team lead 500; the amendment valid from 2026-07-01 says 900 and replaces the limits. "Next week" is after 2026-07-01. 2000 and 3000 are the department-head limits (other row).
## Reference solution
1. search_text "Team lead"; 2. read both sections; use the amendment: 900.
## Why the answer is unique
Amendment replaces the 2025 limits for team lead and department head and is already valid; 500 is retired.
## Teacher result
DeepSeek (r1) searched "Team lead", saw the 2025 table first and answered 500 EUR without reading the later amendment: real model miss, kept as is.''' % (size, o_old, o_new), axes=["LNG", "VER"])
print("ok", size, o_old, o_new)
