# DISTILL-CANARY-41fdeed8 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["调度室/派工单-2026-08-30.csv"])))
repair = [r for r in rows if str(r["工作类型"]).strip() == "检修"]
if len(repair) != 1:
    raise SystemExit("expected exactly one repair work order, found %d" % len(repair))
path = "设备档案/" + str(repair[0]["泵站"]).strip() + ".txt"
if path not in files:
    raise SystemExit("archive file %s is not in the workspace" % path)
print(json.dumps({"expected_string": path}, ensure_ascii=False))
