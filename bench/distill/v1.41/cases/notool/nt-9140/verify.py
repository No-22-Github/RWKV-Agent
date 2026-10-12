# DISTILL-CANARY-340a3b0e : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 0
assert len(case["turns"]) == 2 and case["turns"][0]["prompt"] and case["turns"][1]["prompt"]
print(json.dumps({"expected_contains_any": ["风", "湿度", "体感", "回收站", "无法", "不能", "恢复"]}, ensure_ascii=False))
