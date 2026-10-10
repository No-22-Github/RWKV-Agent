# DISTILL-CANARY-eb95e640 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "api.ludi.example/status" in e.get("url", ""))
line = next(l for l in page["content"].splitlines() if "v1 批量发送" in l)
assert "弃用" in line, "状态行口径异常"
print(json.dumps({"expected_contains_any": ["弃用"]}, ensure_ascii=False))
