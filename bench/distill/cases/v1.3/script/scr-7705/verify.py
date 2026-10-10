# DISTILL-CANARY-0a1908e7 : distillation case
import csv
import io
import json

def build_stdout(entries):
    seen = set()
    per = {}
    for name in sorted(entries):
        if not name.startswith("crossings/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            cid = row["charge_id"]
            if cid in seen:
                continue
            seen.add(cid)
            route = row["route"]
            pax, pence = int(row["passengers"]), int(row["pence"])
            old = per.get(route, (0, 0))
            per[route] = (old[0] + pax, old[1] + pence)
    lines = []
    tp, tm = 0, 0
    for route in sorted(per):
        pax, pence = per[route]
        lines.append(f"{route},{pax},{pence}")
        tp += pax
        tm += pence
    lines.append(f"TOTAL,{tp},{tm}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
