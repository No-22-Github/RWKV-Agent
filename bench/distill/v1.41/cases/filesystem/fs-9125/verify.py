# DISTILL-CANARY-32d907b2 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 21
assert case["files"]["inbox/README.md"].startswith("# Inbox")
assert "never go to processed/" in case["files"]["inbox/README.md"]
out = {}
for name in ["q3-returns", "q3-stock"]:
    text = case["files"]["inbox/%s.csv" % name]
    assert text.startswith("sku,qty" + chr(10)), name
    out["processed/%s.csv" % name] = text
for name in ["q3-sales", "q3-refunds"]:
    assert case["files"]["inbox/%s.csv" % name].startswith("sku,qty")
assert case["files"]["processed/q2-sales.csv"].startswith("sku,qty")
print(json.dumps({"files": out}))
