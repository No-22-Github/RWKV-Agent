# EXAM-CANARY-9090fb1f : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = [l.split(",") for l in case["files"]["data/sales.csv"].splitlines()[1:]]
big = [r for r in rows if r[1] == "North" and int(r[2]) > 200]
out = "order_id,amount\n" + "".join("%s,%s\n" % (r[0], r[2]) for r in big)
print(json.dumps({"expected_number": sum(int(r[2]) for r in big), "files": {"reports/north_big.csv": out}}))
