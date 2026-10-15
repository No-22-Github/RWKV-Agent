# EXAM-CANARY-51d6ac40 : exam gap-fill case
import csv, io, json
from collections import defaultdict
case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["漂流/交接流水.csv"]))
seen = set()
totals = defaultdict(int)
for row in rows:
    entry = tuple(row.items())
    if entry in seen:
        continue
    seen.add(entry)
    totals[row["接收站"]] += int(row["册数"])
out = io.StringIO(newline="")
writer = csv.writer(out, lineterminator="\n")
writer.writerow(["接收站", "接收册数"])
writer.writerows(sorted(totals.items(), key=lambda item: (-item[1], item[0])))
print(json.dumps({"files": {"漂流/接收导入.csv": out.getvalue()}}, ensure_ascii=False))
