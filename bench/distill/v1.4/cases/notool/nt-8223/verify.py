# DISTILL-CANARY-1da20b32 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
import math
assert "250 块" in prompt and "48 块" in prompt
assert math.ceil(250 / 48) == 6
print(json.dumps({"expected_contains_any": ['6 趟', '6趟', '六趟', '6 次', '6次', '跑 6', '6 车', '6车']}, ensure_ascii=False))
