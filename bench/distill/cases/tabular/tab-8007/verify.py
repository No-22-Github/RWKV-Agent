# DISTILL-CANARY-5f5a7cd6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["借阅/2026-09.csv"])))
tot = {}
for r in rows:
    tot[r["分馆"]] = tot.get(r["分馆"], 0) + int(r["册数"])
body = "\n".join("%s,%d" % (b, n) for b, n in sorted(tot.items(), key=lambda x: -x[1]))
print(json.dumps({"files": {"报表/9月借阅汇总.csv": "分馆,册数\n" + body + "\n"}}, ensure_ascii=False))
