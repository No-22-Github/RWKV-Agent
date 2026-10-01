# DISTILL-CANARY-34233150 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["scans/scan-log-2026-09.csv"])))
parcels = {}
rowcount = {}
seen = {}
dups = 0
for r in rows:
    rt = r["route_code"]
    parcels.setdefault(rt, set()).add(r["parcel_id"])
    rowcount[rt] = rowcount.get(rt, 0) + 1
    sig = "|".join(r[c] for c in ("scan_ts", "parcel_id", "depot", "weight_kg", "parcel_note"))
    if r["scan_id"] in seen:
        if seen[r["scan_id"]] != sig:
            raise SystemExit("fixture guard failed: repeated scan_id differs")
        dups += 1
    seen[r["scan_id"]] = sig
if dups < 1:
    raise SystemExit("fixture guard failed: the re-sent scans are gone")
ranked = sorted(parcels.items(), key=lambda kv: (-len(kv[1]), kv[0]))
if len(ranked[1][1]) == len(ranked[0][1]):
    raise SystemExit("fixture guard failed: tie at the top of the parcel ranking")
rows_leader = max(rowcount.items(), key=lambda kv: (kv[1], kv[0]))
if rows_leader[0] == ranked[0][0]:
    raise SystemExit("fixture guard failed: row leader equals parcel leader")
print(json.dumps({"expected": ranked[0][0]}))
