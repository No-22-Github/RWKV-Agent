# DISTILL-CANARY-bcb48bbb : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '17f8b78560f96a78c43ef70d274eeb078e08f0d6fc9564238776dbd031236184', "fixture changed"
print(json.dumps({"files": {'CHANGELOG.md': case['files']['CHANGELOG.md'].replace('# Changelog\n\n## 1.4.0\n- faster startup\n\n## 1.3.2\n- fix crash on empty input\n', '# Changelog\n\n## 1.4.0\n- faster startup\n\n## 1.3.2\n- fix crash on empty input\n\n## 1.4.1\n- fix typo in help text\n')}}, ensure_ascii=False))
