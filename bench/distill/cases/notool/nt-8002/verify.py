# DISTILL-CANARY-c552a987 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "18 箱" in prompt and "24 件" in prompt and "2.5%" in prompt
good = 18 * 24 * (1 - 0.025)
print(json.dumps({"expected_number": int(good)}))
