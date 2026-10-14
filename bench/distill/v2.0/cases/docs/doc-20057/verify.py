# DISTILL-CANARY-5f4b7819 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '637540fea288f08ff622dc516128f729ddfcc04b88f333931a735ca46cb192a3', "fixture changed"
m = re.search('(\\w+): 8 seats', case["files"]['rooms.md'])
assert m and m.group(1) == 'Maple'
print(json.dumps({"expected_string": 'Maple'}, ensure_ascii=False))
