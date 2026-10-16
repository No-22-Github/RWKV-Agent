# DISTILL-CANARY-393bf3e2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fb98253a55a6deca8b47e340f43dc016bc654880ebcd318fd3dd5f2b4d48fc1c', "fixture changed"
import re
m = re.search('电话 (021-5550-2368)', case["files"]['vendor/contact.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
