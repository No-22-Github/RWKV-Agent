# DISTILL-CANARY-d830d4ac : distillation case
import csv
import io
import json

def build_stdout(entries):
    seen = set()
    per = {}
    for name in sorted(entries):
        if not name.startswith("orders/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            oid = row["订单号"]
            if oid in seen:
                continue
            seen.add(oid)
            day = row["日期"]
            amount = int(row["金额分"])
            old = per.get(day, (0, 0))
            per[day] = (old[0] + 1, old[1] + amount)
    lines = []
    to, ta = 0, 0
    for day in sorted(per):
        orders, amount = per[day]
        lines.append(f"{day},{orders},{amount}")
        to += orders
        ta += amount
    lines.append(f"合计,{to},{ta}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
