# DISTILL-CANARY-d9ec6388 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
classes = ["托班", "小班", "中班", "大班"]
for cls in classes:
    assert f[cls + ".csv"].startswith("姓名,月托管费"), cls
assert "月托管费" in f["托管/说明.md"]
chosen = [c for c in classes if c in case["turns"][1]["prompt"]]
assert len(chosen) == 2, chosen
total = 0
for cls in chosen:
    rows = list(csv.DictReader(io.StringIO(f[cls + ".csv"])))
    total += sum(int(r["月托管费"]) for r in rows)
ask = ["哪两个班", "哪几个班", "哪两个班级", "哪些班", "班级名称", "班的名称", "班级编号"]
print(json.dumps({"expected_number": total, "expected_contains_any": ask}, ensure_ascii=False))
