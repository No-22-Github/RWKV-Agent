# DISTILL-CANARY-9a2bb4df : distillation case
import json
case = json.load(open("case.json"))
grams = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "批次,品名,净重克,状态", path
    for row in rows[1:]:
        batch, item, g, status = row.split(",")
        if status == "入库":
            grams += int(g)
print(json.dumps({"expected_string": f"{grams / 1000:.1f}"}))
