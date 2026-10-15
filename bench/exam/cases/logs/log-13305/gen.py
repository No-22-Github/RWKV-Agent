#!/usr/bin/env python3
"""Generates log-13305 (zh, error code of the first ERROR after a deploy marker)."""
import random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, build_log, offsets, check_size, PREFIX

CANARY = "EXAM-CANARY-e46a0c73"
rng = random.Random(13305)
SVCS = ["checkout", "catalog", "pricing", "inventory", "coupon", "shipping-calc"]
MSGS = ["handled request in %dms", "cache refreshed entries=%d", "db pool in use=%d", "feature flags synced count=%d", "metrics flushed points=%d"]
N = 1450
D = int(N * 0.66)
sp = {}
sp[int(N * 0.12)] = ("pricing", "ERROR", "req-3f0a11", "code=E1090 price rule not found")
sp[int(N * 0.35)] = ("coupon", "ERROR", "req-9c2d07", "code=E2210 coupon service unreachable")
sp[int(N * 0.52)] = ("checkout", "ERROR", "req-51b8aa", "code=E4417 payment session expired")
sp[D - 4] = ("inventory", "ERROR", "req-aa04c9", "code=E4417 payment session expired")
sp[D] = ("checkout", "INFO", "req-000000", "deploy v2.8.4 finished, 6/6 instances healthy")
sp[D + 17] = ("shipping-calc", "ERROR", "req-6e19d3", "code=E7302 carrier rate table checksum mismatch")
sp[D + 30] = ("pricing", "ERROR", "req-0b77f5", "code=E1090 price rule not found")
sp[D + 80] = ("coupon", "ERROR", "req-e2a846", "code=E2210 coupon service unreachable")
text = build_log(rng, "# app.log format=v1 host=shop-app-03 date=2026-09-15", N, 20 * 3600, SVCS, MSGS, sp, step=(1, 6), warn=0.05, err=0.0)
size = check_size(text, 80_000, 200_000)
ls = text.splitlines()
mi = next(i for i, l in enumerate(ls) if "deploy v2.8.4 finished" in l)
first = next(l for l in ls[mi:] if " ERROR " in l)
assert "E7302" in first and offsets(text, "E7302")[0] >= PREFIX and offsets(text, "deploy v2.8.4")[0] >= PREFIX
prompt = "昨晚发了 v2.8.4，app.log 里 “deploy v2.8.4 finished” 那一行就是发布完成的时间点。发完之后第一条 ERROR 带的错误码是什么？"
expect = {"output_contains_any": ["E7302"], "output_contains_any_token": True}
finish(HERE, "log-13305", CANARY, "logs", "locate_error", ["TR-LONG", "TR-DECOY"],
       {"TR-LONG": "E1090", "TR-DECOY": "E4417"}, "L2", {"app.log": text}, prompt, expect,
       "Find the first ERROR after a deploy marker deep inside a 100KB+ application log.",
       '''log = case["files"]["app.log"]
assert log.startswith("# app.log format=v1")
ls = log.splitlines()
mi = next(i for i, l in enumerate(ls) if "deploy v2.8.4 finished" in l)
first = next(l for l in ls[mi:] if " ERROR " in l)
print(json.dumps({"expected_contains_any": [re.search(r"code=(E\\d+)", first).group(1)]}))''',
       '''## Traps
- TR-LONG: file is %d bytes; the deploy marker is at byte %d and the answer line at %d, both beyond 65536.
- TR-DECOY: ERRORs before the deploy exist, notably E4417 four lines before the marker (looks like "the" error around deploy time) and E1090/E2210 earlier; the first ERROR in the file is E1090. The answer is the first one after the marker: E7302.
## Reference solution
1. search_text for the deploy marker (line number); 2. read_lines / grep ERROR from there on; first is E7302.
## Why the answer is unique
Single marker line; the next ERROR line in file order carries code=E7302 (noise has no ERRORs by construction).''' % (size, offsets(text, "deploy v2.8.4")[0], offsets(text, "E7302")[0]))
print("ok", size)
