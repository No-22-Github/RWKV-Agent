# DISTILL-CANARY-869f8d99 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
gate = [json.loads(l) for l in files["logs/闸机通行-2026-09.jsonl"].splitlines() if l.strip()]
qr = [json.loads(l) for l in files["logs/二维码通行-2026-09.jsonl"].splitlines() if l.strip()]
assert len(gate) == 90 and len(qr) == 14
assert {(g["site"], g["date"]) for g in gate} == {
    (s, "2026-09-" + str(d).zfill(2)) for s in ("滨江店", "城北店", "大学城店") for d in range(1, 31)}
assert {q["date"] for q in qr} == {"2026-09-" + str(d).zfill(2) for d in range(1, 15)}
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 门禁日志")
assert "没再接进来" in readme and "补传" in readme
total = sum(g["swipes"] for g in gate)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
