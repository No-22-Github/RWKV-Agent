# DISTILL-CANARY-2fe0c6c4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
mapping = {"G": "运行", "Y": "待机", "R": "故障"}
rows = csv.DictReader(io.StringIO(case["files"]["ops/lamp_log.csv"]))
code = next(r["code"] for r in rows if r["device"] == "P-07")
print(json.dumps({"expected_string": mapping[code]}))
