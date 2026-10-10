# DISTILL-CANARY-c4f2fd73 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "JSON" in prompt and "注释" in prompt
assert case["files"]["菜单/配置样例.json"].splitlines()[0] == "{"
print(json.dumps({"expected_contains_any": ["不允许", "不能", "不行", "没有注释", "不支持"]}, ensure_ascii=False))
