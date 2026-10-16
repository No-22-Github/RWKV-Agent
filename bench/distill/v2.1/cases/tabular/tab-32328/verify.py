# DISTILL-CANARY-edcc872e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b787acc55c02366ac9e402fa4c9fb0b8c90aea211faaf65d9f821cf9e20391e5', "fixture changed"
ans = sum(int(l.split(',')[2]) for l in files['exports/2026-09/report_wk2.csv'].splitlines()[1:])
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
