# DISTILL-CANARY-74bfd1d9 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "404" in prompt and "403" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 点单小程序运维说明")
words = ["权限", "找不到", "不存在", "无权访问"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
