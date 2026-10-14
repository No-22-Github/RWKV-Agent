# DISTILL-CANARY-0b80dced : distillation case
import csv, io, json, re

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["docs/生效登记.csv"]))
row = next(r for r in rows
           if r["制度名称"] == "叉车充电区安全守则" and r["状态"] == "现行")
path = "docs/充电守则-" + row["版本"] + "版.md"
text = case["files"][path]
n = re.search(r"不得超过\s*(\d+)\s*小时", text).group(1)
print(json.dumps({"expected_contains_any": [n + " 小时", n + "小时"]}))
