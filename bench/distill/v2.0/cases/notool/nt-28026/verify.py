# DISTILL-CANARY-ffb1f673 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "644" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店终端管理手册")
print(json.dumps({"expected_contains_any": ["读写", "只读", "可读可写", "只可读", "rw-r--r--"]}, ensure_ascii=False))
