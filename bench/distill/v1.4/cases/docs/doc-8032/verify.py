# DISTILL-CANARY-35d33023 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "While supplies last" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 麦丰面点坊 门店文案库")
print(json.dumps({"expected_contains_any": ["售完即止", "售完为止", "送完即止", "卖完即止", "数量有限", "送完为止"]}, ensure_ascii=False))
