# DISTILL-CANARY-1b2a060f : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '680b4642086494da8419c1da62658b0e84ed14a5b02bf86960063bd9d5f8763f', "fixture changed"
m = re.search('(第三方接口联调延期)', case["files"]['周报.md'])
assert m and m.group(1) == '第三方接口联调延期'
m = re.search('(陈总)（负责人）', case["files"]['群成员.md'])
assert m and m.group(1) == '陈总'
print(json.dumps({"expected_string": '第三方接口联调延期'}, ensure_ascii=False))
