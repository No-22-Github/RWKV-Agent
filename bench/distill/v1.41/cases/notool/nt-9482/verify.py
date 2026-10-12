# DISTILL-CANARY-bcd2630d : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["光速", "声速", "光的速度", "声音的速度", "传播速度", "传播得快", "传播得慢", "三秒", "3 秒", "3秒"]}, ensure_ascii=False))
