# DISTILL-CANARY-040ab7aa : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["docs/会员权益表.csv"]))
hits = [r["内容"] for r in rows if r["项目"] == "生日礼券" and r["卡种"] == "白金卡"]
value = hits[0]
number = float(value.replace("元", "").strip())
print(json.dumps({"expected_number": number}))
