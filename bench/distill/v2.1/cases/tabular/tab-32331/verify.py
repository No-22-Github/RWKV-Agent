# DISTILL-CANARY-8ffecb9d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c1aea7864faedb7a21ed39349053ddaa49c1f7b771a6898e2007dbcdcb2e618a', "fixture changed"
ans = sum(1 for l in files['jobs.csv'].splitlines()[1:] if l.split(',')[2] != 'success')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
