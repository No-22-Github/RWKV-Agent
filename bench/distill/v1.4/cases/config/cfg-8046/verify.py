# DISTILL-CANARY-3afb0b97 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert prompt.split("`")[1] == chr(92) + "d"
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 会员编码规范")
print(json.dumps({"expected_contains_any": ["数字", "digit", "0-9"]}, ensure_ascii=False))
