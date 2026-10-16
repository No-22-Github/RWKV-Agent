# DISTILL-CANARY-e7717d66 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '54633c84c6f6e555e22d74430724e4b21902470638a593e4c31c2a219fe0cae8', "fixture changed"
files = case["files"]
assert '3 个工作日' in ' '.join(files.values())
assert '5 个工作日' in ' '.join(files.values())
print(json.dumps({"expected_contains_any": ["过期", "失效", "废弃", "弃用", "作废", "已被替代", "被替代", "被取代", "取代了", "被覆盖", "已覆盖", "覆盖了", "不再", "旧值", "旧版", "过时", "已更新", "已不适用", "不适用", "已停用", "已下线", "已废止", "淘汰", "不是最新", "不是当前", "不是现行", "早于", "已于", "旧的", "老的", "历史", "不是现在", "不是目前", "已经换", "已换", "替换", "停用", "到期", "已结束", "截止", "expired", "Expired", "deprecated", "Deprecated", "outdated", "Outdated", "out of date", "Out of date", "out-of-date", "Out-of-date", "obsolete", "Obsolete", "superseded", "Superseded", "replaced", "Replaced", "no longer", "No longer", "stale", "Stale", "overridden", "Overridden", "overrides", "Overrides", "retired", "Retired", "old value", "Old value", "not current", "Not current", "not valid", "Not valid", "invalid", "Invalid", "legacy", "Legacy", "older", "Older", "earlier", "Earlier", "was valid", "Was valid", "ended", "Ended", "lapsed", "Lapsed", "decommissioned", "Decommissioned", "not the current", "Not the current", "isn't current", "Isn't current", "isn’t current", "Isn’t current", "is not current", "Is not current", "no longer valid", "No longer valid", "previous", "Previous", "prior", "Prior"]}, ensure_ascii=False))
