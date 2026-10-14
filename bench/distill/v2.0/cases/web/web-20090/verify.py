# DISTILL-CANARY-feb7bc23 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '86544e3af3a123b264a7867d6f4fae6ce6f7a81e4093db73e21ade190f53c1c7', "fixture changed"
m = re.search(r"requests==(\S+)", case["files"]["requirements.txt"])
print(json.dumps({"expected_string": m.group(1)}))
