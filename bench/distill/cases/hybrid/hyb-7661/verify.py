# DISTILL-CANARY-1513817b : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["出口部/9月出货明细.csv"]))
boxes = sum(int(str(r["箱数"]).strip()) for r in rows if str(r["目的港"]).strip() == "汉堡")
page = next(e["content"] for e in case["web_fixture"] if "fareast-shipping.example" in e.get("url", ""))
m = re.search(r"汉堡\s*\|\s*([0-9.]+)", page)
if not m:
    raise SystemExit("hamburg rate not found on the notice page")
print(json.dumps({"expected_number": boxes * float(m.group(1))}))
