# DISTILL-CANARY-a018c016 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 52
assert case["files"]["订单/README.md"].startswith("# 订单表")
assert case["files"]["订单/模板.csv"].splitlines()[1].endswith(",待处理")
out = {}
for m in ["07"]:
    path = "订单/2026-%s.csv" % m
    rows = case["files"][path].splitlines()
    assert rows[0] == "单号,客户,金额,状态" and all(not r.endswith(",已受理") for r in rows), path
    out[path] = "".join((r[:-3] + "已受理" if r.endswith(",待处理") else r) + chr(10) for r in rows)
for m in ["08", "09"]:
    rows = case["files"]["订单/2026-%s.csv" % m].splitlines()
    assert rows[0] == "单号,客户,金额,状态" and any(r.endswith(",待处理") for r in rows)
print(json.dumps({"files": out}, ensure_ascii=False))
