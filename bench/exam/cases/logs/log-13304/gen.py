#!/usr/bin/env python3
"""Generates log-13304 (en, count one error kind from one worker after a marker line)."""
import random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, build_log, offsets, check_size, PREFIX

CANARY = "EXAM-CANARY-b2e7149d"
rng = random.Random(13304)
SVCS = ["worker-b1", "worker-b2", "worker-b3", "worker-b4", "scheduler", "coordinator"]
MSGS = ["task batch-%d claimed", "task batch-%d completed", "checkpoint written seq=%d", "heartbeat sent lag=%dms", "shard rebalance planned moves=%d"]
ERRS = ["lease expired for shard", "checkpoint write timed out", "payload too large, skipped", "lease expired for shard", "unknown shard id"]
N = 1500
M = int(N * 0.62)
sp = {M: ("coordinator", "INFO", "req-000000", "config reload applied (rev 41) workers=4")}
text = build_log(rng, "# batch.log format=v2 cluster=batch-eu date=2026-09-15", N, 2 * 3600, SVCS, MSGS, sp,
                 step=(2, 9), warn=0.03, err=0.22, err_msgs=ERRS)
size = check_size(text, 80_000, 200_000)
lines = text.splitlines()
mi = next(i for i, l in enumerate(lines) if "config reload applied" in l)
assert offsets(text, "config reload applied")[0] >= PREFIX


def n(ls):
    return sum(1 for l in ls if "[worker-b3] ERROR" in l and "lease expired" in l)


ans, total, pre = n(lines[mi:]), n(lines), n(lines[: max(1, text[:PREFIX].count("\n"))])
assert ans != total and ans != pre and ans >= 5 and total - ans >= 5, (ans, total, pre)
prompt = ("We pushed a config reload to the batch cluster this morning, it's the 'config reload applied' line in batch.log. "
          "Since that reload, how many times has worker-b3 logged a 'lease expired' error? Just the number is fine.")
expect = {"expected_number": ans, "tolerance": 0.001, "expected_number_in_text": True}
finish(HERE, "log-13304", CANARY, "logs", "count_events", ["TR-LONG", "TR-DECOY"],
       {"TR-LONG": pre, "TR-DECOY": total}, "L2", {"batch.log": text}, prompt, expect,
       "Count one worker's one error kind after a marker line in a 100KB+ log.",
       '''log = case["files"]["batch.log"]
assert log.startswith("# batch.log format=v2")
ls = log.splitlines()
mi = next(i for i, l in enumerate(ls) if "config reload applied" in l)
print(json.dumps({"expected": sum(1 for l in ls[mi:] if "[worker-b3] ERROR" in l and "lease expired" in l)}))''',
       '''## Traps
- TR-LONG: file is %d bytes; the reload marker is at byte %d (> 65536), so everything that counts is past the first page. Counting only the first page gives %d.
- TR-DECOY: counting every worker-b3 "lease expired" error in the whole file gives %d; other workers also log the same error; worker-b3 also logs other ERROR kinds.
## Reference solution
1. search_text `config reload applied` to find the line; 2. count matching lines after it (bash: sed -n '<line>,$p' | grep -c ...).
## Why the answer is unique
Exactly one marker line; the answer is %d lines after it that are ERROR from [worker-b3] with "lease expired".''' % (size, offsets(text, "config reload applied")[0], pre, total, ans))
print("ok", size, ans, total, pre)
