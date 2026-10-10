# DISTILL-CANARY-7aa40052 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0] == "# 澄泉净水 保修文档"
terms = files["条款/保修条款-第3版.md"].splitlines()
sect = []
cur = None
for l in terms:
    if l.startswith("## "):
        cur = l
    if l.startswith("（编写说明"):
        break
    if cur == "## 商用机型":
        sect.append(l)
assert not any("上门费" in l for l in sect)
assert any("定价中" in l for l in terms)
assert any("不另计费" in l for l in terms)
assert any("上门费条款" in l and "商务部" in l for l in files["条款/版本记录.md"].splitlines())
words = ["定价中", "没有写", "未写", "还没写", "待定", "补充", "未定"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
