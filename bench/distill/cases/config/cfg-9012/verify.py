# DISTILL-CANARY-f95c7737 : distillation case
import json, re
case = json.load(open("case.json"))
text = case["files"]["服务/结算/超时.yaml"]
assert text.startswith("# 结算服务覆盖")
print(json.dumps({"expected_number": int(re.search(r"读超时秒: ([0-9]+)", text).group(1))}))
