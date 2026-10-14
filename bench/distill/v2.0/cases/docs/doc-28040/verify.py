# DISTILL-CANARY-05635043 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "JSON" in prompt and "单引号" in prompt
assert case["files"]["菜单/配置样例.json"].splitlines()[0] == "{"
print(json.dumps({"expected_contains_any": ["双引号", "double quote", "Double quote"]}, ensure_ascii=False))
