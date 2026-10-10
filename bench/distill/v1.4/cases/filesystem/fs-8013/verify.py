# DISTILL-CANARY-b26da9a2 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0] == "# 麦禾烘焙 门店运营资料"
note = files["检查表/登记说明.md"]
assert "小程序" in note and "不再归档" in note
sheets = [p for p in files if p.startswith("检查表/")]
assert "检查表/9月检查表-模板.md" in sheets
assert not any(p.startswith("检查表/2026-09") for p in files)
tpl = files["检查表/9月检查表-模板.md"]
assert "模板" in tpl and "未填写" in tpl
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "不再归档", "模板"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
