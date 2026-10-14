# DISTILL-CANARY-8cd6feba : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "售罄" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店文案库")
print(json.dumps({"expected_contains_any": ["sold out", "sold-out", "out of stock", "run out of"]}))
