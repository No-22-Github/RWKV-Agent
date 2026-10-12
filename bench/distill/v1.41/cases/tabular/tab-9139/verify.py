# DISTILL-CANARY-807d58e4 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 1116
assert case["files"]["流水/说明.md"].startswith("# 流水说明")
n = 0
for path, text in case["files"].items():
    if path.startswith("流水/") and path.endswith(".csv"):
        rows = text.splitlines()
        assert rows[0] == "日期,品类,数量,类型", path
        for r in rows[1:]:
            d, c, q, k = r.split(",")
            n += int(q) * (c == "奶茶" and k == "退货")
print(json.dumps({"expected_number": n}))
