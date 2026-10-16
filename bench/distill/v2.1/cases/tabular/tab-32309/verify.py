# DISTILL-CANARY-467fd8a5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '383f34d469aa4b368c99ad1b2287306d4ad07ed7529b21d08e059158038932db', "fixture changed"
ans = sum(int(l.split(',')[2].lstrip('¥')) for l in files['expenses.csv'].splitlines()[1:])
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
