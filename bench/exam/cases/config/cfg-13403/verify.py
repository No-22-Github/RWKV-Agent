# EXAM-CANARY-fcfa536a : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]
missing = ["coupon_amount"]
anchors = {"schema/order.yaml": "table: orders", "schema/refund.yaml": "table: refunds"}
for path, first in anchors.items():
    assert path in files and files[path].lstrip().startswith(first), "fixture damaged: " + path
blob = "\n".join(v for k, v in files.items() if k not in []) + json.dumps(case.get("web_fixture", []), ensure_ascii=False)
for item in missing:
    assert item not in blob.replace("{", "").replace("}", "") or False, item
for item in missing:
    assert item not in files, item
print(json.dumps({"expected": "UNKNOWN", "must_state_unverified": missing}, ensure_ascii=False))
