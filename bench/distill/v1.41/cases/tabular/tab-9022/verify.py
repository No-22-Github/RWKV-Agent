# DISTILL-CANARY-d6463727 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["ledgers/README.md"].startswith("# Q3 ledgers")
assert "cartons of 12 units" in case["files"]["ledgers/README.md"]
cartons = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "sku,cartons,type,date", path
    for row in rows[1:]:
        sku, qty, kind, day = row.split(",")
        if sku == "ALU-10" and kind == "receipt":
            cartons += int(qty)
units = cartons * 12
print(json.dumps({"expected_contains_any": [str(units), f"{units:,}"]}))
