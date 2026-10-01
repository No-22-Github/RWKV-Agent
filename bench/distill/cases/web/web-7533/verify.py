# DISTILL-CANARY-77893668 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "open.banxia.example/notices" in e.get("url", ""))
line = next(l for l in page["content"].splitlines() if "v2 接口的停用时间" in l)
assert ("推迟" in line or "延期" in line), "公告口径与题面判据不一致"
print(json.dumps({"expected_contains_any": ["延期", "推迟", "延后", "延长", "照常", "仍可", "仍能", "还能"]}, ensure_ascii=False))
