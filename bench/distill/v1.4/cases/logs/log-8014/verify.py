# DISTILL-CANARY-9618c02b : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
# sabotage guard: bank verify deletes the first non-empty line of this file first
assert files["logs/云归档-2026-10.log"].splitlines()[0] == "小橡树亲子摄影 云相册归档日志"

log = files["logs/云归档-2026-10.log"].splitlines()
task = [l for l in log if " TASK " in l]
assert len(task) == 1 and task[0].startswith("2026-10-04")
manual = [l for l in log if l.startswith("2026-10-05") and " MANUAL " in l]
assert len(manual) == 4
assert any("自动归档任务暂停" in l for l in log)
doc = files["运维/云相册迁移说明.md"]
assert "暂停" in doc and "手动" in doc
words = ["暂停", "迁移", "手动", "MANUAL", "没有运行", "未运行", "没运行", "没有跑", "没跑", "停用", "没有执行", "未执行", "不再", "没有自动"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
