# DISTILL-CANARY-1d1db732 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "国庆节" in prompt
print(json.dumps({"expected_contains_any": ['10 月 1 日', '10月1日', '十月一日', '10 月 1 号', '10月1号']}, ensure_ascii=False))
