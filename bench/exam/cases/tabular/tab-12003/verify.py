# EXAM-CANARY-d9f31e7b : exam gap-fill case
import csv, io, json
from collections import defaultdict
case = json.load(open("case.json", encoding="utf-8"))
totals = defaultdict(int)
for row in csv.DictReader(io.StringIO(case["files"]["讲堂/预约.csv"])):
    totals[row["场次"]] += int(row["人数"])
out = io.StringIO(newline="")
writer = csv.writer(out, lineterminator="\n")
writer.writerow(["场次", "占用座位"])
writer.writerows(sorted(totals.items(), key=lambda item: (-item[1], item[0])))
print(json.dumps({"files": {"讲堂/座位导入.csv": out.getvalue()}}, ensure_ascii=False))
