# DISTILL-CANARY-b2daea16 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
price = {r["sku"]: float(r["list_price"]) for r in csv.DictReader(io.StringIO(f["catalog/items.csv"])) if r["category"] == "Accessories"}
total = round(sum(price[r["sku"]] * int(r["qty"]) for r in csv.DictReader(io.StringIO(f["inventory/stock.csv"])) if r["sku"] in price), 2)
strip = lambda v: v.rstrip("0").rstrip(".")
print(json.dumps({"expected_contains_any": sorted({strip("%.2f" % total), strip("{:,.2f}".format(total))})}))
