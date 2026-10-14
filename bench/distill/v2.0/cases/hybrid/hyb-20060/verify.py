# DISTILL-CANARY-d92809e2 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ea76e4bc6c9031c38a88edc3f702d698aecf351cfc64139f6f5ee0a94aa5be39', "fixture changed"
m = re.search('(E-5021)', case["files"]['incident.md'])
assert m and m.group(1) == 'E-5021'
m = re.search('Vendor: (Corvid)', case["files"]['incident.md'])
assert m and m.group(1) == 'Corvid'
print(json.dumps({"expected_string": 'E-5021'}, ensure_ascii=False))
