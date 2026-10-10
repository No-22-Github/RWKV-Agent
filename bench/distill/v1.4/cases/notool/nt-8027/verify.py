# DISTILL-CANARY-b6358276 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "git fetch" in prompt and "git pull" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店终端管理手册")
print(json.dumps({"expected_contains_any": ["合并", "merge", "拉取并合并"]}, ensure_ascii=False))
