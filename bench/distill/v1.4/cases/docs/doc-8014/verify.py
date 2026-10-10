# DISTILL-CANARY-ea847c08 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0] == "# 麦禾烘焙 工艺文档库"
spec = files["规范/全麦吐司工艺规范.md"]
assert "## 6 冷却与切片" not in spec and "补写中" in spec
log = files["规范/修订记录.md"]
assert any("冷却与切片" in l and "补写中" in l for l in log.splitlines())
inspect = files["规范/全麦吐司品控检验规范.md"]
assert "12 mm" in inspect and "品控检验" in inspect
words = ["补写", "起草", "未定稿", "还没写", "没有写", "尚未", "编写中"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
