# DISTILL-CANARY-d0adff87 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 587
assert case["files"]["明细/README.md"].startswith("# 销售明细")
assert case["files"]["汇总/2026-08.txt"].splitlines()[1].startswith("华东 ")
n = 0
for path, text in case["files"].items():
    if path.startswith("明细/2026-"):
        rows = text.splitlines()
        assert rows[0] == "区域,品类,销售额", path
        n += sum(int(r.split(",")[2]) for r in rows[1:] if r.split(",")[0] == "华东")
aug = int(case["files"]["汇总/2026-08.txt"].splitlines()[1].split()[1])
print(json.dumps({"expected_contains_any": [str(aug), format(aug, ","), str(n), format(n, ",")]}))
