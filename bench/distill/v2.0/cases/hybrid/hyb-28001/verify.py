# DISTILL-CANARY-e294339b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["船队/疏浚船.csv"])))
total = sum(int(r["总吨"]) for r in rows if r["状态"] == "在役")
official = [w for w in case["web_fixture"] if "dongyu-port.gov.cn" in w["url"]][0]
assert official.get("error")
print(json.dumps({"expected_number": total}))
