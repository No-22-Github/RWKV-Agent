# DISTILL-CANARY-8b1c5caf : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
assert files['rides/2026-09.csv'].splitlines()[0] == 'date,vehicle_model,rides'
assert files['fleet/model-register.csv'].splitlines()[0] == 'model,bikes,status,note'
ledger = list(csv.DictReader(io.StringIO(files['rides/2026-09.csv'])))
status = list(csv.DictReader(io.StringIO(files['fleet/model-register.csv'])))
assert ledger and set(ledger[0]) == set('date,vehicle_model,rides'.split(","))
assert not any(r['vehicle_model'] == 'Swift-9' for r in ledger)
codes = {r['model']: r for r in status}
row = codes['Swift-9']
assert row['status'] == 'withdrawn' and 'Swift-10' in row['note']
decoy = sum(float(r['rides']) for r in ledger if r['vehicle_model'] == 'Swift-10')
exp = case["turns"][0]["expect"]["output_excludes"]
n = int(round(decoy))
want = [str(n), "{:,}".format(n)]
assert all(w in exp for w in want)
print(json.dumps({"expected_contains_any": ['not listed', "isn't listed", 'no entry', "doesn't list", 'does not list', 'not in the', 'not on the', 'no row', 'missing', 'not covered', 'recalled', 'withdrawn', 're-fitted', 'refitted']}, ensure_ascii=False))
