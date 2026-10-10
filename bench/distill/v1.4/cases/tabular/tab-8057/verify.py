# DISTILL-CANARY-994c16bc : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["游泳馆/票务/国庆场次.csv"].startswith("日期,场次,入场组数,票房收入")
assert "票房收入单位为元" in f["游泳馆/说明.md"]
rows = list(csv.DictReader(io.StringIO(f["游泳馆/票务/国庆场次.csv"])))
m = re.search(r"(\d+)\s*月\s*(\d+)\s*日", case["turns"][1]["prompt"])
day = "10-%02d" % int(m.group(2))
sess = "下午场" if "下午场" in case["turns"][1]["prompt"] else "上午场"
hits = [r for r in rows if r["日期"] == day and r["场次"] == sess]
assert len(hits) == 1, hits
ask = ["哪一场", "哪个场次", "哪一场次", "哪一天的哪一场", "具体场次", "场次名称", "哪个时段"]
print(json.dumps({"expected_number": int(hits[0]["票房收入"]),
                  "expected_contains_any": ask}, ensure_ascii=False))
