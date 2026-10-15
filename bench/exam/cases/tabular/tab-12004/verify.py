# EXAM-CANARY-7b082fea : exam gap-fill case
import csv, io, json, re
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
case = json.load(open("case.json", encoding="utf-8"))
text = case["files"]["社区/补助导入说明.md"]
rates = {kind: (Decimal(rate) / 100, Decimal(cap)) for kind, rate, cap in re.findall(r"^([^,\n]+),(\d+)%,(\d+\.\d+)$", text, re.M)}
totals = defaultdict(Decimal)
for row in csv.DictReader(io.StringIO(case["files"]["社区/场地活动.csv"])):
    paid = Decimal(row["实付费用"].replace("¥", "").replace(",", ""))
    rate, cap = rates[row["类别"]]
    grant = min(paid * rate, cap).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    totals[row["场地"]] += grant
out = io.StringIO(newline="")
writer = csv.writer(out, lineterminator="\n")
writer.writerow(["场地", "核定补助（元）"])
writer.writerows((place, format(amount, ".2f")) for place, amount in sorted(totals.items(), key=lambda item: (-item[1], item[0])))
print(json.dumps({"files": {"社区/补助导入.csv": out.getvalue()}}, ensure_ascii=False))
