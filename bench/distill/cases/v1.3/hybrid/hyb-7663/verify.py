# DISTILL-CANARY-d4ba30fe : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
seen = set()
total = 0
for key in ("采购/华东订单.csv", "采购/华南订单.csv"):
    for r in csv.DictReader(io.StringIO(case["files"][key])):
        no = str(r["采购单号"]).strip()
        if no in seen:
            continue
        seen.add(no)
        if str(r["型号"]).strip() == "XQ-500":
            total += int(str(r["数量"]).strip())
page = next(e["content"] for e in case["web_fixture"] if "quanxin-machine.example" in e.get("url", ""))
m = re.search(r"XQ-500\s*\|\s*([0-9.]+)", page)
if not m:
    raise SystemExit("XQ-500 price not found on the quote page")
print(json.dumps({"expected_number": total * float(m.group(1))}))
