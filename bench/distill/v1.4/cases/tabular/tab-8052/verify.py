# DISTILL-CANARY-1612d538 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
for path in ("托管/餐费/九月上旬.csv", "托管/餐费/九月中旬.csv", "托管/餐费/九月下旬.csv"):
    assert f[path].startswith("班级,日期,加餐项目,金额"), path
assert "按旬" in f["托管/餐费/说明.md"]
prompt = case["turns"][1]["prompt"]
chosen = [p for p in f if p.endswith(".csv") and p in prompt]
assert len(chosen) == 1, chosen
rows = list(csv.DictReader(io.StringIO(f[chosen[0]])))
total = round(sum(float(r["金额"]) for r in rows), 2)
ask = ["哪一份", "哪份", "哪个文件", "文件名", "文件路径", "文件的路径"]
print(json.dumps({"expected_contains_any": ask +
                  [("%.2f" % total).rstrip("0").rstrip("."),
                   "{:,.2f}".format(total).rstrip("0").rstrip(".")]}, ensure_ascii=False))
