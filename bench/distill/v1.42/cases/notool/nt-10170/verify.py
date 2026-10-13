# DISTILL-CANARY-e6b5fcc5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0af48bbff66c40ae2213d1df9d5118701a44fb9472c8f37b941761cdb5557eae', "fixture changed"
print(json.dumps({"expected_contains_any": ["tar -xzf", "tar xzf", "tar -zxf", "tar zxf", "tar -xvzf", "tar xvzf", "tar -zxvf", "tar zxvf"]}, ensure_ascii=False))
