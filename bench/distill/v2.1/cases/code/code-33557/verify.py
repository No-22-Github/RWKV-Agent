# DISTILL-CANARY-71e83fe1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a511f9a936e45bd9a2f8e90669de5007f6f57e3e1914a215f6eda907ac011ccf', "fixture changed"
ns = {}
for p in ['text/dedupe.py']:
    exec(files[p], ns)
ans = str(eval('dedupe_sorted([5, 3, 5, 1, 3])', ns))
assert str(ans) == '[1, 3, 5]', ans

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
