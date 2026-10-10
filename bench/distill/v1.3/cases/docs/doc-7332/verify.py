# DISTILL-CANARY-9a62fe56 : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["布草换洗登记.csv"]))
rooms = [r["房间"] for r in rows if r["加急"] == "是" and r["状态"] != "已送回"]
print(json.dumps({"expected_contains_any": rooms}))
