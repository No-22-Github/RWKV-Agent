# DISTILL-CANARY-9e3afe45 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0] == "# 澄泉净水 售后知识库"
faq = files["售后/FAQ.md"]
entries = [l for l in faq.splitlines() if l.startswith("## ")]
assert "## 台式净饮机 X3" not in entries
assert "## 台式净饮机 X3 Pro" in entries
listing = files["售后/收录型号.md"]
assert any("X3" in l and "补录" in l for l in listing.splitlines())
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "补录", "还没有", "暂无"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
