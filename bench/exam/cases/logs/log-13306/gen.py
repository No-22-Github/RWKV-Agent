#!/usr/bin/env python3
"""Generates log-13306 (en, JSONL access log: distinct users rate-limited on one endpoint)."""
import json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, PREFIX

CANARY = "EXAM-CANARY-07d9a5b2"
rng = random.Random(13306)
PATHS = ["/v2/items", "/v2/orders", "/v2/export", "/v2/search", "/v2/profile", "/v2/reports/summary"]
N = 1350
users = ["u-%04d" % rng.randrange(1000, 9999) for _ in range(140)]
burst_users = users[:19]
rows = []
sec = 9 * 3600
for i in range(N):
    sec += rng.randrange(1, 5)
    p = PATHS[rng.randrange(len(PATHS))]
    u = users[rng.randrange(len(users))]
    st = 200 if rng.random() < 0.93 else rng.choice([404, 500, 304])
    if i > N * 0.12 and rng.random() < 0.03:
        st = 429                                  # other paths get throttled too (decoy)
    if p == "/v2/export" and i > N * 0.62 and rng.random() < 0.55:
        st, u = 429, burst_users[rng.randrange(len(burst_users))]
    elif p == "/v2/export" and st == 429:
        st = 200
    if i < N * 0.10 and p == "/v2/export" and rng.random() < 0.3:
        st, u = 429, users[100 + rng.randrange(10)]     # a few early export throttles by other users
    rows.append(json.dumps({"ts": "2026-09-15T%02d:%02d:%02dZ" % (sec // 3600, sec // 60 % 60, sec % 60), "user": u,
                            "method": "GET", "path": p, "status": st, "ms": rng.randrange(8, 900)}))
text = "\n".join(rows) + "\n"
size = check_size(text, 80_000, 200_000)


def distinct(ls):
    return len({json.loads(l)["user"] for l in ls if json.loads(l)["status"] == 429 and json.loads(l)["path"] == "/v2/export"})


ls = text.splitlines()
ans = distinct(ls)
pre_lines = text[:PREFIX].count("\n")
pre = distinct(ls[:pre_lines])
raw = sum(1 for l in ls if json.loads(l)["status"] == 429 and json.loads(l)["path"] == "/v2/export")
assert pre != ans and raw != ans and 10 <= ans <= 40, (ans, pre, raw)
prompt = ("api-access.jsonl is yesterday's access log for the public API. Some clients got throttled (HTTP 429) on the export endpoint. "
          "How many different users were hit by that? Just the number.")
expect = {"expected_number": ans, "tolerance": 0.001, "expected_number_in_text": True}
finish(HERE, "log-13306", CANARY, "logs", "aggregate_jsonl", ["TR-LONG", "TR-DECOY"],
       {"TR-LONG": pre, "TR-DECOY": raw}, "L2", {"api-access.jsonl": text}, prompt, expect,
       "Count distinct users throttled on one endpoint in a 100KB+ JSONL access log.",
       '''rows = [json.loads(l) for l in case["files"]["api-access.jsonl"].splitlines() if l.strip()]
print(json.dumps({"expected": len({r["user"] for r in rows if r["status"] == 429 and r["path"] == "/v2/export"})}))''',
       '''## Traps
- TR-LONG: file is %d bytes (%d lines); most export throttling happens in the second half, past the first 64KB. Using only the first page gives %d distinct users.
- TR-DECOY: counting 429 lines on /v2/export instead of distinct users gives %d; 429s also occur on other paths (counting them all is another wrong answer).
## Reference solution
1. bash/jq style: filter status==429 and path=="/v2/export", unique user, count. (2 calls.)
## Why the answer is unique
Distinct user ids with status 429 and path exactly /v2/export = %d (computed in gen.py and re-derived in verify.py).''' % (size, len(ls), pre, raw, ans))
print("ok", size, ans, pre, raw)
