# DISTILL-CANARY-9706584d : distillation case
import json
case = json.load(open("case.json"))
rb = case["files"]["tools/buyers.rb"]
assert "state == 'paid'" in rb and "seen.size" in rb
buyers = set()
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "order,customer,state", path
    for row in rows[1:]:
        order, customer, state = row.split(",")
        if state == "paid":
            buyers.add(customer)
print(json.dumps({"expected_contains_any": [str(len(buyers))]}))
