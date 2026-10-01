# DISTILL-CANARY-ef611618 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["出口部/出港记录.csv"]))
boxes = sum(int(str(r["箱数"]).strip()) for r in rows if str(r["目的港"]).strip() == "鹿特丹")
page = next(e["content"] for e in case["web_fixture"] if "wanli-shipping.example/notices" in e.get("url", ""))
m = re.search(r"鹿特丹\s*\|\s*([0-9.]+)", page)
if not m:
    raise SystemExit("rotterdam rate not found on the notice page")
print(json.dumps({"expected_number": boxes * float(m.group(1))}))
