# DISTILL-CANARY-723812d5 : distillation case
import csv
import io
import datetime
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["aftersale/orders.csv"]))
received = next(r["received_date"] for r in rows if r["order_no"] == "MD-3312")
recv = datetime.date.fromisoformat(received)
req = datetime.date(2026, 3, 10)  # request date stated in the prompt
within = (req - recv).days <= 7
print(json.dumps({"expected_string": "在期限内" if within else "已超期"}))
