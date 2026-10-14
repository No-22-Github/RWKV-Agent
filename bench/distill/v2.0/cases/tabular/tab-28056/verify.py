# DISTILL-CANARY-47805424 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
assert f["游泳馆/会员/剩余课时.csv"].startswith("姓名,卡种,剩余课时")
assert "最小单位 0.5" in f["游泳馆/说明.md"]
rows = list(csv.DictReader(io.StringIO(f["游泳馆/会员/剩余课时.csv"])))
names = [r["姓名"] for r in rows]
assert len(set(names)) == len(names)
hits = [r for r in rows if r["姓名"] in case["turns"][1]["prompt"]]
assert len(hits) == 1, hits
ask = ["哪个孩子", "哪位学员", "哪个姓名", "孩子叫什么", "学员的姓名", "孩子的姓名", "学员姓名", "孩子的名字", "学员编号"]
print(json.dumps({"expected_number": float(hits[0]["剩余课时"]),
                  "expected_contains_any": ask}, ensure_ascii=False))
