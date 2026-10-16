# DISTILL-CANARY-00f2cfd6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2575af24172d2f636c192d07bee6b6275531206598d794c4625f6434043dd676', "fixture changed"
import re
m = re.search('迁移推到 (10 月 12 日)', case["files"]['notes/meeting-0915.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
