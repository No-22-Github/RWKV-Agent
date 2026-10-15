# EXAM-CANARY-a4ce6902 : exam gap-fill case
import csv, io, json, re
from collections import defaultdict
case = json.load(open("case.json", encoding="utf-8"))
coefficients = {name: int(value) for name, value in re.findall(r"^(\S+) = (-?\d+)$", case["files"]["器材/面板导入说明.md"], re.M)}
totals = defaultdict(int)
for row in csv.DictReader(io.StringIO(case["files"]["器材/借还.csv"])):
    totals[row["柜组"]] += int(row["件数"]) * coefficients[row["动作"]]
out = io.StringIO(newline="")
writer = csv.writer(out, lineterminator="\n")
writer.writerow(["柜组", "净外借件数"])
writer.writerows(sorted(totals.items(), key=lambda item: (-item[1], item[0])))
print(json.dumps({"files": {"器材/净外借导入.csv": out.getvalue()}}, ensure_ascii=False))
