# DISTILL-CANARY-d3c7b2c5 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "URL" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 麦丰面点坊 门店系统速查")
print(json.dumps({"expected_contains_any": ["统一资源定位", "网址", "地址"]}, ensure_ascii=False))
