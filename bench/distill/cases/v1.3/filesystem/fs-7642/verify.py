# DISTILL-CANARY-dfde4bb6 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["客户资料/合同索引.csv"])))
match = [r for r in rows if str(r["合同编号"]).strip() == "HT-2026-0317"]
if len(match) != 1:
    raise SystemExit("expected one row for HT-2026-0317, found %d" % len(match))
path = "客户资料/" + str(match[0]["文件名"]).strip()
if path not in files:
    raise SystemExit("indexed scan file %s is not in the workspace" % path)
print(json.dumps({"expected_string": path}, ensure_ascii=False))
