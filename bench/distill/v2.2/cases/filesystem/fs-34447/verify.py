# DISTILL-CANARY-9a33b594 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '819f3da0e35fd0322b6da8ab21b7ee5edcc651c518346f2e3bc7e20dfbd3558d', "fixture changed"
py = {p: files[p].count('\n') for p in files if p.endswith('.py')}
m = sorted(py, key=lambda p: -py[p])
assert py[m[0]] > py[m[1]] + 5
answers = [sum(py.values()), [m[0].split('/')[-1]]]

print(json.dumps({"expected_string": answers[1][0]}, ensure_ascii=False))
