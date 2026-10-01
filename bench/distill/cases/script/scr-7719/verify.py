# DISTILL-CANARY-c9253b17 : distillation case
import csv
import io
import json

def build_stdout(entries):
    seen = set()
    per = {}
    for name in sorted(entries):
        if not name.startswith("tickets/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            tid = row["ticket_id"]
            if tid in seen:
                continue
            seen.add(tid)
            if row["status"] != "open":
                continue
            repairer = row["repairer"]
            per[repairer] = per.get(repairer, 0) + 1
    lines = []
    total = 0
    for repairer in sorted(per):
        lines.append(f"{repairer},{per[repairer]}")
        total += per[repairer]
    lines.append(f"TOTAL,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
