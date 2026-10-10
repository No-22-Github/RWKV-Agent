# DISTILL-CANARY-d5d6dab0 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["网关/限流.yaml"].splitlines()
assert lines[0] == "默认:"
i = lines.index("  /orders:")
block = {}
for l in lines[i + 1:]:
    if not l.startswith("    "):
        break
    k, v = l.strip().split(":", 1)
    block[k] = v.strip()
assert block["超限返回"] == "503"
print(json.dumps({"expected_number": int(block["每秒放行"])}))
