# DISTILL-CANARY-6daf3804 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/sessions-2026-09.csv"])))
drivers = {}
rowcount = {}
seen = {}
dups = 0
for r in rows:
    st = r["site_code"]
    drivers.setdefault(st, set()).add(r["driver_code"])
    rowcount[st] = rowcount.get(st, 0) + 1
    sig = "|".join(r[c] for c in ("session_date", "driver_code", "kwh", "connector", "session_note"))
    if r["session_id"] in seen:
        if seen[r["session_id"]] != sig:
            raise SystemExit("fixture guard failed: repeated session_id differs")
        dups += 1
    seen[r["session_id"]] = sig
if dups < 1:
    raise SystemExit("fixture guard failed: the re-sent sessions are gone")
ranked = sorted(drivers.items(), key=lambda kv: (-len(kv[1]), kv[0]))
if len(ranked[1][1]) == len(ranked[0][1]):
    raise SystemExit("fixture guard failed: tie at the top of the driver ranking")
rows_leader = max(rowcount.items(), key=lambda kv: (kv[1], kv[0]))
if rows_leader[0] == ranked[0][0]:
    raise SystemExit("fixture guard failed: row leader equals driver leader")
print(json.dumps({"expected": ranked[0][0]}))
