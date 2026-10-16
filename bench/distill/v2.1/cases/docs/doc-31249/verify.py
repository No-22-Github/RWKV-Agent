# DISTILL-CANARY-f24f6eca : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '95604ee39e92a4ea17b8e0e2219e1272db1faafbe8793e77537ad435ab2ec0d7', "fixture changed"
files = case["files"]
assert '25 日' in ' '.join(files.values())
assert '20 日' in ' '.join(files.values())
print(json.dumps({"expected_contains_any": ["过期", "失效", "废弃", "弃用", "作废", "已被替代", "被替代", "被取代", "取代了", "被覆盖", "已覆盖", "覆盖了", "不再", "旧值", "旧版", "过时", "已更新", "已不适用", "不适用", "已停用", "已下线", "已废止", "淘汰", "不是最新", "不是当前", "不是现行", "早于", "已于", "旧的", "老的", "历史", "不是现在", "不是目前", "已经换", "已换", "替换", "停用", "到期", "已结束", "截止", "expired", "Expired", "deprecated", "Deprecated", "outdated", "Outdated", "out of date", "Out of date", "out-of-date", "Out-of-date", "obsolete", "Obsolete", "superseded", "Superseded", "replaced", "Replaced", "no longer", "No longer", "stale", "Stale", "overridden", "Overridden", "overrides", "Overrides", "retired", "Retired", "old value", "Old value", "not current", "Not current", "not valid", "Not valid", "invalid", "Invalid", "legacy", "Legacy", "older", "Older", "earlier", "Earlier", "was valid", "Was valid", "ended", "Ended", "lapsed", "Lapsed", "decommissioned", "Decommissioned", "not the current", "Not the current", "isn't current", "Isn't current", "isn’t current", "Isn’t current", "is not current", "Is not current", "no longer valid", "No longer valid", "previous", "Previous", "prior", "Prior"]}, ensure_ascii=False))
