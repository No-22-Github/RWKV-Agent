# DISTILL-CANARY-143d8e83 : distillation case
import csv
import io
import json

def build_stdout(entries):
    per = {}
    for name in sorted(entries):
        if not name.startswith("receipts/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            day = row["日期"]
            slips, pence = int(row["笔数"]), int(row["金额分"])
            old = per.get(day, (0, 0))
            per[day] = (old[0] + slips, old[1] + pence)
    lines = []
    ts, tp = 0, 0
    for day in sorted(per):
        slips, pence = per[day]
        lines.append(f"{day},{slips},{pence}")
        ts += slips
        tp += pence
    lines.append(f"合计,{ts},{tp}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
