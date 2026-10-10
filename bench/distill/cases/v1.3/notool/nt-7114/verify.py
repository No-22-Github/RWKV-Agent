# DISTILL-CANARY-abe691da : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["intake/batches_2026-10.csv"])))
status = next(r["状态码"] for r in rows if r["批次"] == "B2610-01")
print(json.dumps({"expected_string": "能" if status == "A" else "不能"}, ensure_ascii=False))
