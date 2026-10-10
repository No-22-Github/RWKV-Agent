# DISTILL-CANARY-c0091698 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "ops.tiema.example/codes" in e.get("url", ""))
row = next(l for l in page["content"].splitlines() if l.startswith("E-2203 "))
assert "过期" in row, "E-2203 行含义异常"
print(json.dumps({"expected_contains_any": ["过期"]}, ensure_ascii=False))
