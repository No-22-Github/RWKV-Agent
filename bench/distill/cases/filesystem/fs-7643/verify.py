# DISTILL-CANARY-0ed20d62 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["车间日报归档/日报导出台账.csv"])))
match = [r for r in rows if str(r["日期"]).strip() == "2026-08-12"]
if len(match) != 1:
    raise SystemExit("expected one ledger row dated 2026-08-12, found %d" % len(match))
path = "车间日报归档/" + str(match[0]["导出文件"]).strip()
if path not in files:
    raise SystemExit("ledger points at %s which is not in the workspace" % path)
print(json.dumps({"expected_string": path}, ensure_ascii=False))
