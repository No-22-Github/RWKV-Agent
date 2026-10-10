# DISTILL-CANARY-1294c450 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
t = dict(l.split(": ", 1) for l in files["工单/GD-0732.txt"].splitlines() if ": " in l)
assert t["变更项"] == "告警上限"
lines = files["配置/冷库探头.yaml"].splitlines(keepends=True)
out = []
for l in lines:
    if l.startswith(t["变更项"] + ": "):
        old = l.split(": ", 1)[1].split()[0]
        l = l.replace(": " + old + " ", ": " + t["新值"] + " ", 1)
    out.append(l)
print(json.dumps({"files": {"配置/冷库探头.yaml": "".join(out)}}, ensure_ascii=False))
