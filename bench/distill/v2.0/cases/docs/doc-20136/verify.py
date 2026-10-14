# DISTILL-CANARY-0170510f : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b900d7fcce26ba25abd61cfe8da33843b502e2544f5097f47a04b928ef81e062', "fixture changed"
print(json.dumps({"files": {'README.md': case['files']['README.md'].replace('# 部署指南 v1.2\n\n当前版本 v1.2，升级请见下表。\n| 版本 | 说明 |\n| v1.2 | 稳定 |\n旧版 v1.1 不再维护。\n', '# 部署指南 v1.3\n\n当前版本 v1.3，升级请见下表。\n| 版本 | 说明 |\n| v1.3 | 稳定 |\n旧版 v1.1 不再维护。\n')}}, ensure_ascii=False))
