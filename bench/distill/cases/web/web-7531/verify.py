# DISTILL-CANARY-fff32453 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "docs.yusheng.example/sdk/errors" in e.get("url", ""))
row = next(l for l in page["content"].splitlines() if l.startswith("14029 "))
assert "占用" in row, "14029 行含义异常"
print(json.dumps({"expected_contains_any": ["占用"]}, ensure_ascii=False))
