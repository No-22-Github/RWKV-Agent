# DISTILL-CANARY-3d83754c : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
bits = re.search(r"`([01]+)`", prompt).group(1)
value = int(bits, 2)
assert value == 11
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门禁权限说明")
print(json.dumps({"expected_number": value}))
