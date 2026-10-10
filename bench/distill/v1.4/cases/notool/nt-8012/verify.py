# DISTILL-CANARY-6676ca19 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "503" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店终端运维")
words = ["不可用", "过载", "维护", "暂时"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
