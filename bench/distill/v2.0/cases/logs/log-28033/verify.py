# DISTILL-CANARY-3c55cb41 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
main = [json.loads(l) for l in files["logs/新风主楼-2026-09.jsonl"].splitlines() if l.strip()]
swim = [json.loads(l) for l in files["logs/新风游泳馆-2026-09.jsonl"].splitlines() if l.strip()]
assert len(main) == 30 and len(swim) == 17
assert {m["date"] for m in main} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {s["date"] for s in swim} == {"2026-09-" + str(d).zfill(2) for d in range(1, 18)}
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 新风机组运行日志")
assert "还没导出" in readme and "10 月 5 日" in readme
total = sum(m["run_minutes"] for m in main)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
