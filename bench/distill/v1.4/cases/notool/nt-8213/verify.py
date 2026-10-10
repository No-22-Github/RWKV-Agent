# DISTILL-CANARY-9aa31c59 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "warranty" in prompt
print(json.dumps({"expected_contains_any": ['收据', '小票', '发票', '凭证', '购物凭证']}, ensure_ascii=False))
