# DISTILL-CANARY-bf19aceb : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
md = case["files"]["finance/cleaning-rates-2026.md"]
std = float(re.search(r"Standard sites: \$([\d.]+) per visit", md).group(1))
crew = float(re.search(r"two-person crew: \$([\d.]+) per visit", md).group(1))
roster_line = re.search(r"Medical roster for July: (.+)", md).group(1)
roster = {s.strip() for s in roster_line.split(",")}
rows = list(csv.DictReader(io.StringIO(case["files"]["invoices/july-2026.csv"])))
def bill(site):
    visits = int(next(x for x in rows if x["site"] == site)["visits"])
    rate = crew if site in roster else std
    return round(visits * rate, 2)
t1 = bill("Pellworth Clinic")
t2 = bill("Hargrave House")
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
