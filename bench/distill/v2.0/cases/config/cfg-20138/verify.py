# DISTILL-CANARY-1b2a78bc : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '83acef16976a9fc60abc50a0f68ba8057f5cbac6b8d2a67690bf5be02ecff515', "fixture changed"
print(json.dumps({"files": {'app.env': case['files']['app.env'].replace('LOG_LEVEL=INFO\nDEBUG_SQL=1\nPORT=9000\n', 'LOG_LEVEL=WARN\nPORT=9000\n')}}, ensure_ascii=False))
