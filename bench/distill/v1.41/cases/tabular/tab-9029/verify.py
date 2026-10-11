# DISTILL-CANARY-2f0a8037 : distillation case
import json
case = json.load(open("case.json"))
readme = case["files"]["meters/README.md"]
assert readme.startswith("# Meter readings")
rows = case["files"]["meters/readings.csv"].splitlines()
declared = int(readme.split(", ")[1].split(" rows")[0])
assert rows[0] == "ts,meter,kwh,flag" and len(rows) - 1 == declared, (len(rows), declared)
tenths = 0
for row in rows[1:]:
    ts, meter, kwh, flag = row.split(",")
    if meter == "M-204" and flag != "void":
        tenths += int(kwh.replace(".", ""))
value = f"{tenths // 10}.{tenths % 10}"
print(json.dumps({"expected_contains_any": [value, f"{tenths // 10:,}.{tenths % 10}"]}))
