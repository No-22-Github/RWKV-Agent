# DISTILL-CANARY-46dce989 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "gate.xiushan.example/codes" in e.get("url", ""))
row = next(l for l in page["content"].splitlines() if l.startswith("G-3112 "))
assert "监护人" in row, "G-3112 行含义异常"
print(json.dumps({"expected_contains_any": ["监护人"]}, ensure_ascii=False))
