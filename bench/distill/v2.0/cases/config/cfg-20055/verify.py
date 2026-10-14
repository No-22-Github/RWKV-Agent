# DISTILL-CANARY-747237ef : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2105e2c6a4e488cccebdcb24f11afb2bbd8b97295ab0cce60e826801ca119765', "fixture changed"
m = re.search('oncall:\\s*([\\w.@-]+)', case["files"]['notify.yaml'])
assert m and m.group(1) == 'sre-oncall@corp.example'
m = re.search('(3 failed)', case["files"]['last_run.txt'])
assert m and m.group(1) == '3 failed'
print(json.dumps({"expected_string": 'sre-oncall@corp.example'}, ensure_ascii=False))
