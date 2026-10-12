# DISTILL-CANARY-46f5203e : distillation case
import json
case = json.load(open("case.json"))
LINES = {'传感器/甲站.tsv': 80, '传感器/乙站.tsv': 71, '传感器/丙站.tsv': 70, '传感器/丁站.tsv': 68, '传感器/说明.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"]["传感器/说明.md"].startswith("# 传感器说明")
best = None
stations = 0
for path, text in case["files"].items():
    if not path.endswith(".tsv"):
        continue
    stations += 1
    rows = text.splitlines()
    assert rows[0] == "时间\t指标\t数值\t状态", path
    for row in rows[1:]:
        f = row.split("\t")
        assert len(f) == 4, row
        if f[1] == "PM2.5":
            best = max(best or 0, int(f[2]))
assert stations == 4
print(json.dumps({"expected_number": best}))
