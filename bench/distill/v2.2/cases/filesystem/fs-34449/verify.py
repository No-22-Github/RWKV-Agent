# DISTILL-CANARY-faed7265 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd2b42103750b3d18eb9f80723e91943073c488466f44cce3e08891b2eb6c8be8', "fixture changed"
c = [p for p in files if '/vendor/' not in p]
m = max(c, key=lambda p: len(files[p].encode()))
assert len(files[m].encode()) > 1700 and len(files[sorted(c, key=lambda p: -len(files[p].encode()))[1]].encode()) < 1700
answers = [[m.split('/')[-1]], len(files[m].encode())]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
