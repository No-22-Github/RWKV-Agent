# DISTILL-CANARY-53c1e80e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5f44fdd85ce7d3882a8f3c4d245d9f698e4f17253116003f6290db4907dfbba8', "fixture changed"
ns = {}
for p in ['contacts/phone.py']:
    exec(files[p], ns)
ans = str(eval("normalize('0044 (20) 7946-0011')", ns))
assert str(ans) == '+442079460011', ans

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
