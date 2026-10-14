# DISTILL-CANARY-a88332b5 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '53a09428cb93bf79ffb0dea8dc327fde8c07dc4b507c94f16b162890ddc3efd8', "fixture changed"
m = re.search('\\[staging\\]\\s*host=([\\d.]+)', case["files"]['servers.ini'])
assert m and m.group(1) == '10.20.3.15'
print(json.dumps({"expected_string": '10.20.3.15'}, ensure_ascii=False))
