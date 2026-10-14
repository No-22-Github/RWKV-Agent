# DISTILL-CANARY-1c6ae4ac : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '888890a1504e105797667b89457b5517393181277b87525136e5c55efb1ba137', "fixture changed"
m = re.search('(14:00)', case["files"]['meeting.md'])
assert m and m.group(1) == '14:00'
m = re.search('(zhou\\.lan@[\\w.]+)', case["files"]['contacts.csv'])
assert m and m.group(1) == 'zhou.lan@lanting.example'
print(json.dumps({"expected_string": '14:00'}, ensure_ascii=False))
