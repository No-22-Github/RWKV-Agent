# DISTILL-CANARY-72515672 : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["物料库存.csv"]))
lines = ["# 补货公告", "", "以下物料库存低于安全库存，请按缺口补齐：", ""]
for r in rows:
    if float(r["库存数"]) < float(r["安全库存"]):
        gap = int(float(r["安全库存"]) - float(r["库存数"]))
        lines.append("- {}：缺 {} {}".format(r["物料"], gap, r["单位"]))
content = "\n".join(lines) + "\n"
print(json.dumps({"files": {"公告/补货公告.md": content}}))
