# DISTILL-CANARY-adaf171e : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/lightboard-1017.log"].splitlines() if l.strip()]
interrupted = [l for l in lines if "中断演出" in l]
backup = [l for l in lines if "备用面板" in l]
firmware = [l for l in lines if "固件" in l and "工单" in l]
if not interrupted or not backup or not firmware:
    raise SystemExit(1)
facts = [
    interrupted[0].split()[1],
    "备用面板",
    "固件",
]
print(json.dumps({"expected_contains_any": facts}))
