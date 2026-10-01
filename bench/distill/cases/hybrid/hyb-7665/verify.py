# DISTILL-CANARY-dae56591 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["集装箱部/装箱清单.csv"]))
n = sum(1 for r in rows if str(r["尺寸"]).strip() == "20GP")
base_page = next(e["content"] for e in case["web_fixture"] if "price-list" in e.get("url", ""))
sur_page = next(e["content"] for e in case["web_fixture"] if "surcharge" in e.get("url", ""))
m1 = re.search(r"20GP\s*\|\s*([0-9.]+)", base_page)
m2 = re.search(r"20GP\s*\|\s*([0-9.]+)", sur_page)
if not m1 or not m2:
    raise SystemExit("20GP rate missing from one of the carrier pages")
print(json.dumps({"expected_number": n * (float(m1.group(1)) + float(m2.group(1)))}))
