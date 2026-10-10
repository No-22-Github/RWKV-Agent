# DISTILL-CANARY-0249ed80 : distillation case
import csv
import io
import json

def build_stdout(entries):
    per = {}
    for name in sorted(entries):
        if not name.startswith("sales/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            product = row["product"]
            trays, loaves = int(row["trays"]), int(row["loaves"])
            old = per.get(product, (0, 0))
            per[product] = (old[0] + trays, old[1] + loaves)
    lines = []
    gt, gl = 0, 0
    for product in sorted(per):
        trays, loaves = per[product]
        lines.append(f"{product},{trays},{loaves}")
        gt += trays
        gl += loaves
    lines.append(f"GRAND,{gt},{gl}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
