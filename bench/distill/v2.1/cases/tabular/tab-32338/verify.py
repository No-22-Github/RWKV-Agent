# DISTILL-CANARY-a5fe2647 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'efa0dc500599eadc6cefda0aa95d10d3dc663f015e68381ac46d8a66c7cc31a4', "fixture changed"
import datetime
ans = sum(1 for l in files['orders_aug.csv'].splitlines()[1:] if datetime.date.fromisoformat(l.split(',')[1]).isoweekday() >= 6)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
