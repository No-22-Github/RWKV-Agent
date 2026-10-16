# DISTILL-CANARY-2b62869f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c3f1227ac14719f509d2d01b48ba059dfc056c0c1f3ec1b61558d7aee903b4e6', "fixture changed"
import re
m = re.search("'(/v2/refunds)'", case["files"]['server/routes.py'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
