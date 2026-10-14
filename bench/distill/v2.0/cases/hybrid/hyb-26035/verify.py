# DISTILL-CANARY-700d4f0e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["takings/july-2026.csv"])))
nets = {}
for r in rows:
    s = r["stall"]
    nets.setdefault(s, [0.0, 0.0])
    nets[s][0] += float(r["takings"])
    nets[s][1] += float(r["wastage"])
net = {s: round(v[0] - v[1], 2) for s, v in nets.items()}
t1 = net["Ostler Dairy"]
t2 = max(net, key=net.get)
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 in case["turns"][1]["expect"]["output_equals_any"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
