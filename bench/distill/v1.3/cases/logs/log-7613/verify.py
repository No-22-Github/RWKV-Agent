# DISTILL-CANARY-5b084f27 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/drip-0711.log"].splitlines() if l.strip()]
faults = [l for l in lines if "故障" in l and "手动测试" not in l]
shutoff = [l for l in lines if "手动关闭" in l]
if not faults or not shutoff:
    raise SystemExit(1)
note = case["files"]["notes/维修记录.md"]
if "电磁阀" not in note:
    raise SystemExit(1)
facts = [
    faults[0].split()[1],
    shutoff[0].split()[1],
    "电磁阀",
]
print(json.dumps({"expected_contains_any": facts}))
