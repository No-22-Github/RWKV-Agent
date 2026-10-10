# DISTILL-CANARY-322721e1 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
gw = [json.loads(l) for l in files["logs/网关确认-2026-09.jsonl"].splitlines() if l.strip()]
sms = [json.loads(l) for l in files["logs/短信确认-2026-09.jsonl"].splitlines() if l.strip()]
assert len(gw) == 30 and len(sms) == 26
assert {g["date"] for g in gw} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
have = {"2026-09-" + str(d).zfill(2) for d in list(range(1, 9)) + list(range(13, 31))}
missing = {"2026-09-" + str(d).zfill(2) for d in range(9, 13)}
assert {s["date"] for s in sms} == have and not (have & missing)
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# 私教约课确认日志")
assert "磁盘故障" in readme and "补回" in readme
total = sum(g["confirmed"] for g in gw)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
