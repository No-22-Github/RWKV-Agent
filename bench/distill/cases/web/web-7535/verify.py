# DISTILL-CANARY-de33eaf5 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "open.banxia.example/status" in e.get("url", ""))
row = next(l for l in page["content"].splitlines() if l.startswith("sms.send "))
assert "弃用" in row, "sms.send 状态行异常"
print(json.dumps({"expected_contains_any": ["弃用"]}, ensure_ascii=False))
