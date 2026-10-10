# DISTILL-CANARY-37ac261a : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
gw = [json.loads(l) for l in files["logs/约课网关-2026-09.jsonl"].splitlines() if l.strip()]
leg = [json.loads(l) for l in files["logs/旧版通道-2026-09.jsonl"].splitlines() if l.strip()]
assert len(gw) == 30 and len(leg) == 18
assert {g["date"] for g in gw} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {g["date"] for g in leg} == {"2026-09-" + str(d).zfill(2) for d in range(1, 19)}
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 约课服务日志")
assert "代收" in readme and "归档" in readme
total = sum(g["ok"] + g["failed"] for g in gw)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
