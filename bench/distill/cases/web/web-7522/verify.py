# DISTILL-CANARY-b81e8504 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "help.yunfan.example/export" in e.get("url", ""))
line = next(l for l in page["content"].splitlines() if "对账单导出默认" in l)
assert "xlsx" in line, "默认格式行里没有 xlsx"
print(json.dumps({"expected_contains_any": ["xlsx"]}, ensure_ascii=False))
