#!/usr/bin/env python3
"""Generates log-13303 (zh, busiest ERROR minute inside one hour of a 7h app log)."""
import random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, offsets, check_size, PREFIX

CANARY = "EXAM-CANARY-81c4e6b9"
rng = random.Random(13303)
SVCS = ["web-api", "job-runner", "image-proxy", "mailer", "search-index", "session-store"]
INFO = ["handled GET /feed 200 in %dms", "job sync-catalog finished in %dms", "thumbnail cache hit key=%d",
        "mail queued id=%d", "index segment merged docs=%d", "session renewed ttl=%ds"]
ERRS = ["upstream timeout after 3000ms", "database connection reset", "failed to decode payload", "disk quota exceeded on /var/spool"]
WARNS = ["retrying after transient failure", "slow query 1840ms", "queue backlog above threshold"]
lines = []


def emit(h, m, lvl, msg):
    svc = SVCS[rng.randrange(len(SVCS))]
    lines.append("2026-09-15 %02d:%02d:%02d %-5s [%s] %s" % (h, m, rng.randrange(60), lvl, svc, msg))


BURSTS = {(1, 12): ("ERROR", 12), (5, 8): ("WARN", 15), (5, 37): ("ERROR", 9), (3, 50): ("ERROR", 11)}
for h in range(0, 7):
    for m in range(60):
        n = rng.randrange(3, 7)
        errs = 0
        for _ in range(n):
            r = rng.random()
            if r < 0.04 and errs < 2:
                errs += 1
                emit(h, m, "ERROR", ERRS[rng.randrange(len(ERRS))])
            elif r < 0.10:
                emit(h, m, "WARN", WARNS[rng.randrange(len(WARNS))])
            else:
                t = INFO[rng.randrange(len(INFO))]
                emit(h, m, "INFO", t % rng.randrange(5, 900) if "%" in t else t)
        if (h, m) in BURSTS:
            lvl, k = BURSTS[(h, m)]
            for _ in range(k):
                emit(h, m, lvl, (ERRS if lvl == "ERROR" else WARNS)[rng.randrange(3)])
body = sorted(lines, key=lambda s: s[:19])
text = "# app.log format=v1 host=app-07 date=2026-09-15\n" + "\n".join(body) + "\n"
size = check_size(text, 80_000, 200_000)
assert min(offsets(text, "2026-09-15 05:")) >= PREFIX
cnt = {}
for ln in body:
    if ln[11:13] == "05" and " ERROR " in ln:
        cnt[ln[11:16]] = cnt.get(ln[11:16], 0) + 1
best = sorted(cnt.items(), key=lambda kv: -kv[1])
assert best[0][0] == "05:37" and best[0][1] > best[1][1] + 3, best[:3]
prompt = "app.log 是昨天凌晨到早上的应用日志，我想看看早上 5 点那一个小时里，报 ERROR 最集中的是哪一分钟？告诉我几点几分就行。"
expect = {"output_contains_any": ["05:37", "5:37", "5点37", "5 点 37"], "output_contains_any_token": True}
finish(HERE, "log-13303", CANARY, "logs", "time_window", ["TR-LONG", "TR-DECOY"],
       {"TR-LONG": "01:12", "TR-DECOY": "05:08"}, "L2", {"app.log": text}, prompt, expect,
       "Find the busiest ERROR minute in the 05:00 hour of a 7-hour application log.",
       '''log = case["files"]["app.log"]
assert log.startswith("# app.log format=v1")
cnt = {}
for ln in log.splitlines()[1:]:
    if ln[11:13] == "05" and " ERROR " in ln:
        cnt[ln[11:16]] = cnt.get(ln[11:16], 0) + 1
top = max(cnt.values())
winners = [k for k, v in cnt.items() if v == top]
assert len(winners) == 1
w = winners[0]
print(json.dumps({"expected_contains_any": [w, w.lstrip("0"), "%d点%d" % (int(w[:2]), int(w[3:])), "%d 点 %d" % (int(w[:2]), int(w[3:]))]}, ensure_ascii=False))''',
       '''## Traps
- TR-LONG: file is %d bytes; the whole 05:xx hour sits after byte %d (> 65536), so the first page shows only 00:00-02:xx.
- TR-DECOY: 01:12 has 12 ERROR lines (global-looking peak, in the first 64KB); 05:08 has a burst of 15 WARN lines (busiest minute of the hour if levels are not distinguished); 03:50 has an ERROR burst of 11. The answer is only the busiest ERROR minute within 05:00-05:59.
## Reference solution
1. grep ERROR lines for `2026-09-15 05:` and count per minute. 2. pick the top minute: 05:37 (9 extra ERROR lines; other 05:xx minutes have at most 2).
## Why the answer is unique
Noise minutes are capped at 2 ERROR lines; 05:37 has at least 9, so the top is strict (asserted in gen.py).''' % (size, min(offsets(text, "2026-09-15 05:"))))
print("ok", size)
