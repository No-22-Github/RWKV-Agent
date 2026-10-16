# DISTILL-CANARY-9fe34060 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '050869eb06bb6d13855013e13fa0d264faebb600fbbf2bb04afd4cc5afd9ba6c', "fixture changed"
ans = sum(1 for l in files['sales_2026-09.csv'].splitlines()[1:] if l.split(',')[1] == '2026/09/15')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
