# DISTILL-CANARY-af5fbddb : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {"日志/app-2026-10-01.log": "2026-10-01 ERROR boom\n", "日志/app-2026-10-02.log": "2026-10-02 ERROR boom\n"}
print(json.dumps({"expected_contains_any": ["grep -c", "grep"]}, ensure_ascii=False))
