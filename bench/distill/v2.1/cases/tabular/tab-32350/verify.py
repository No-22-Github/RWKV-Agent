# DISTILL-CANARY-f927a400 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '55089d7f6e7e76e35e7503bc3e037dbcccefb891e0d8aaa8c684688262f96acd', "fixture changed"
ans = str(sorted(int(l.split(',')[1]) for l in files['latency.csv'].splitlines()[1:])[150])
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
