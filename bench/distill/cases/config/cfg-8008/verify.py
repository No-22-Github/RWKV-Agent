# DISTILL-CANARY-e0462e9b : distillation case
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("支付网关路由配置")
lines = case["files"]["网关/路由.yaml"].splitlines(keepends=True)
start = lines.index("  /pay:\n")
end = next(i for i in range(start + 1, len(lines)) if not lines[i].startswith("    "))
for i in range(start + 1, end):
    key = lines[i].strip().split(":")[0]
    if key in ("连接超时秒", "读超时秒", "写超时秒"):
        lines[i] = "    %s: 5\n" % key
print(json.dumps({"files": {"网关/路由.yaml": "".join(lines)}}, ensure_ascii=False))
