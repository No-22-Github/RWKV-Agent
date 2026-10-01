# DISTILL-CANARY-a17f4c08 : p13 holdout (eval-only)
import csv
import io
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
stock_rows = list(csv.DictReader(io.StringIO(case["files"]["stock/current.csv"])))
guide = case["files"]["stock-guide.md"]
points = {}
for m in re.finditer(r"- (\S+): reorder at (\d+), order (\d+)", guide):
    points[m.group(1)] = (int(m.group(2)), int(m.group(3)))
lines = []
for row in stock_rows:
    sku = row["sku"]
    if sku in points and int(row["on_hand"]) < points[sku][0]:
        lines.append("2026-09-24 RESTOCK %s x%d" % (sku, points[sku][1]))
content = case["files"]["logs/restock-log.txt"] + "\n".join(lines) + "\n"
print(json.dumps({"files": {
    "logs/restock-log.txt": content,
    "stock-guide.md": case["files"]["stock-guide.md"],
    "stock/current.csv": case["files"]["stock/current.csv"],
}}))
