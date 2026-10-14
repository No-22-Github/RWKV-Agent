# DISTILL-CANARY-32719251 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ac3494af226662fac152ff56c3b8b23f1fa6379525c0c5c09e6065e04de8b0a8', "fixture changed"
m = re.search('# (Day-1 Checklist)', case["files"]['checklist.md'])
assert m and m.group(1) == 'Day-1 Checklist'
print(json.dumps({"expected_string": 'Day-1 Checklist'}, ensure_ascii=False))
