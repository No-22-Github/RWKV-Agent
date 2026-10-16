# DISTILL-CANARY-a2980cb3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bfd7e725d4ed64cc294360149a45cfafbbb7a6c9d4bcc6bf7687f413e8368c4b', "fixture changed"
files = case["files"]
blob = ' '.join(files.values())
assert '1000 元' in blob
assert '800 元' in blob
print(json.dumps({"expected_contains_any": ["冲突", "不一致", "矛盾", "不同", "出入", "不符", "分歧", "不一样", "对不上", "各写", "各自", "两个值", "两处", "两份", "不统一", "有差异", "存在差异", "差异", "说法不一", "两种说法", "互相", "conflict", "Conflict", "inconsistent", "Inconsistent", "disagree", "Disagree", "differ", "Differ", "mismatch", "Mismatch", "discrepan", "Discrepan", "contradict", "Contradict", "doesn't match", "Doesn't match", "doesn’t match", "Doesn’t match", "don't match", "Don't match", "don’t match", "Don’t match", "does not match", "Does not match", "do not match", "Do not match", "not consistent", "Not consistent", "two different", "Two different", "different values", "Different values", "differently", "Differently", "conflicting", "Conflicting", "inconsistency", "Inconsistency", "优先", "为准", "以", "覆盖", "生效", "采用", "胜出", "precedence", "Precedence", "priority", "Priority", "takes priority", "Takes priority", "overrid", "Overrid", "wins", "Wins", "takes effect", "Takes effect", "effective", "Effective", "authoritative", "Authoritative", "prevails", "Prevails"]}, ensure_ascii=False))
