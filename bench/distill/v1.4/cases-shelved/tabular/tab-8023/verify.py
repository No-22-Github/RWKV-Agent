# DISTILL-CANARY-e977a5c8 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
assert files['rides/2026-09.csv'].splitlines()[0] == 'date,zone,revenue_eur'
assert files['zones/zones.csv'].splitlines()[0] == 'zone_id,zone,status,note'
ledger = list(csv.DictReader(io.StringIO(files['rides/2026-09.csv'])))
status = list(csv.DictReader(io.StringIO(files['zones/zones.csv'])))
assert ledger and set(ledger[0]) == set('date,zone,revenue_eur'.split(","))
assert not any(r['zone'] == 'Alder Walk' for r in ledger)
codes = {r['zone']: r for r in status}
row = codes['Alder Walk']
assert row['status'] == 'merged' and 'Alder Park' in row['note']
decoy = sum(float(r['revenue_eur']) for r in ledger if r['zone'] == 'Alder Park')
exp = case["turns"][0]["expect"]["output_excludes"]
want = ["%.2f" % decoy, "{:,.2f}".format(decoy)]
assert all(w in exp for w in want)
print(json.dumps({"expected_contains_any": ['not listed', "isn't listed", 'no entry', "doesn't list", 'does not list', 'not in the', 'not on the', 'no row', 'missing', 'not covered', 'merged', 'redrawn', 'folded']}, ensure_ascii=False))
