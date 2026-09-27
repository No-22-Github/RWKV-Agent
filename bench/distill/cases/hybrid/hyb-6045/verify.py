# DISTILL-CANARY-95397497 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
md = case["files"]["docs/staging-terms-2026.md"]
levy_rate = float(re.search(r"Craft section exhibitors pay a ([\d.]+)% staging levy", md).group(1)) / 100
rows = list(csv.DictReader(io.StringIO(case["files"]["invoices/exhibitors-2026.csv"])))
def owed(exhibitor):
    r = next(x for x in rows if x["exhibitor"] == exhibitor)
    fee = float(r["booth_fee"])
    refund = float(r["refund"])
    if r["section"] == "Craft":
        return round((fee - refund) * (1 + levy_rate), 2)
    return round(fee - refund, 2)
t1 = owed("Colvend Pottery")
t2 = owed("Dunbreck Weavers")
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
