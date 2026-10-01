# DISTILL-CANARY-ab373964 : distillation case
import csv, io, json, re

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["docs/退货订单.csv"]))
row = next(r for r in rows if r["订单号"] == "TB-1104")
text = case["files"]["docs/退货政策.md"]
if "教材" in row["品类"] or "教辅" in row["品类"]:
    n = re.search(r"教材[^\n]*?(\d+)\s*天", text).group(1)
else:
    n = re.search(r"签收之日起\s*(\d+)\s*天", text).group(1)
print(json.dumps({"expected_number": float(n)}))
