# DISTILL-CANARY-4c381fe3 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.DictReader(io.StringIO(case["files"]["物业/抄表记录.csv"])))
meter = [r for r in rows if str(r["房号"]).strip() == "2-101"]
if len(meter) != 1:
    raise SystemExit("expected one meter row for 2-101, found %d" % len(meter))
usage = int(str(meter[0]["本月读数"]).strip()) - int(str(meter[0]["上月读数"]).strip())
page = next(e["content"] for e in case["web_fixture"] if "guixiangyuan.example" in e.get("url", ""))
m = re.search(r"合表电价\s*\|\s*([0-9.]+)", page)
if not m:
    raise SystemExit("pool tariff not found on the notice page")
print(json.dumps({"expected_number": usage * float(m.group(1))}))
