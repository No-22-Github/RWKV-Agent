#!/usr/bin/env python3
"""Generates doc-13316 (en, internal handbook: client SDK default timeout, 3.x section vs 4.x section)."""
import random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, offsets
from _doc import make_doc

CANARY = "EXAM-CANARY-1b6d8f45"
rng = random.Random(13316)
OLD = ["## Client SDK defaults (3.x series)", "", "Published: 2025-02-10", "",
       "The internal client SDK (`harborkit`) ships with these defaults in the 3.x series:", "",
       "| Setting | Default |", "|---|---|",
       "| request_timeout | 30 seconds |", "| max_retries | 3 |", "| pool_size | 10 |", "",
       "Teams may override every value per client instance."]
NEW = ["## Client SDK defaults (4.x series, supersedes 3.x)", "", "Published: 2026-06-02", "",
       "Starting with 4.0 the defaults were tightened after the March incident review. The 3.x table above no longer applies to any 4.x release, including 4.2:", "",
       "| Setting | Default |", "|---|---|",
       "| request_timeout | 12 seconds |", "| max_retries | 2 |", "| pool_size | 20 |", "",
       "Overrides per client instance still work as before."]
text = make_doc(rng, "en", "Internal Platform Handbook", 82, {26: OLD, 72: NEW})
size = check_size(text, 30_000, 60_000)
o_old, o_new = offsets(text, "Published: 2025-02-10")[0], offsets(text, "Published: 2026-06-02")[0]
assert o_new >= 40_000 and o_old < o_new
prompt = "Our services are on harborkit 4.2. What is the default request timeout the SDK uses if we don't set one ourselves? It's in platform-handbook.md. Just the number of seconds is fine."
expect = {"expected_number": 12, "tolerance": 0.001, "expected_number_in_text": True}
finish(HERE, "doc-13316", CANARY, "docs", "policy_lookup", ["TR-LONG", "TR-SUPERSEDE"],
       {"TR-LONG": 30, "TR-SUPERSEDE": 30}, "L2", {"platform-handbook.md": text}, prompt, expect,
       "Find the 4.x default timeout in a 50KB handbook that also has a 3.x defaults table.",
       '''import re as _re
doc = case["files"]["platform-handbook.md"]
assert doc.startswith("# Internal Platform Handbook")
best = None
for sec in doc.split("\\n## "):
    d = _re.search(r"Published: (\\d{4}-\\d{2}-\\d{2})", sec)
    v = _re.search(r"\\| request_timeout \\| (\\d+) seconds \\|", sec)
    if d and v and (best is None or d.group(1) > best[0]):
        best = (d.group(1), int(v.group(1)))
print(json.dumps({"expected": best[1]}))''',
       '''## Traps
- TR-LONG: handbook is %d bytes (within the spec's 30-60KB range, so the whole file fits one 64KB read); 3.x table at byte %d, 4.x section at byte %d.
- TR-SUPERSEDE: the 3.x table (published 2025-02-10) says 30 seconds. The 4.x section (published 2026-06-02) says 12 seconds and explicitly says the 3.x table does not apply to 4.2. The user is on 4.2.
## Reference solution
1. search_text request_timeout; 2. read both sections; 4.x applies: 12.
## Why the answer is unique
The prompt pins the version (4.2); the 4.x section covers every 4.x release; 30 is the 3.x value.''' % (size, o_old, o_new), axes=["LNG", "VER"])
print("ok", size, o_old, o_new)
