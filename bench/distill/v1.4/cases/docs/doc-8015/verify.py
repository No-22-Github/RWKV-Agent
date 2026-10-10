# DISTILL-CANARY-125cf694 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0] == "# 麦禾烘焙 门店开业手册"
manual = files["手册/门店开业手册.md"]
assert "## 4 试营业首日预案" not in manual and "编写中" in manual
plan = files["手册/中秋档期预案.md"]
assert "260 盒" in plan
words = ["编写中", "还没写", "没有写", "未完成", "补写", "起草", "尚未"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
