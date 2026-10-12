# DISTILL-CANARY-1b2766f3 : distillation case
import json, re
case = json.load(open("case.json"))
text = case["files"]["服务/风控/限流.toml"]
assert text.startswith("# 风控服务覆盖")
print(json.dumps({"expected_number": int(re.search(r"qps = ([0-9]+)", text).group(1))}))
