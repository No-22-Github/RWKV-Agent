# DISTILL-CANARY-3e9e9923 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '970492a3d81f2a0cabc7db234590d281f81f8d8e94ad423b24e34e1f259541c0', "fixture changed"
page = case["web_fixture"][0]["content"]
assert case["files"]['采购/云存储.md'].startswith('# 云存储选型')
assert '0.08' in page
print(json.dumps({"expected_contains_any": ["0.08"]}, ensure_ascii=False))
