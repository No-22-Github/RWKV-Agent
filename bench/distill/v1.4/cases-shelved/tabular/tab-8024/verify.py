# DISTILL-CANARY-f2dd7d21 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
assert files['maintenance/2026-09.csv'].splitlines()[0] == 'work_order,date,depot,cost_eur'
assert files['depots/depots.csv'].splitlines()[0] == 'depot_id,depot,status,note'
ledger = list(csv.DictReader(io.StringIO(files['maintenance/2026-09.csv'])))
status = list(csv.DictReader(io.StringIO(files['depots/depots.csv'])))
assert ledger and set(ledger[0]) == set('work_order,date,depot,cost_eur'.split(","))
assert not any(r['depot'] == 'Kestrel Yard' for r in ledger)
codes = {r['depot']: r for r in status}
row = codes['Kestrel Yard']
assert row['status'] == 'retired' and 'Kestrel Yard East' in row['note']
decoy = sum(float(r['cost_eur']) for r in ledger if r['depot'] == 'Kestrel Yard East')
exp = case["turns"][0]["expect"]["output_excludes"]
want = ["%.2f" % decoy, "{:,.2f}".format(decoy)]
assert all(w in exp for w in want)
print(json.dumps({"expected_contains_any": ['not listed', "isn't listed", 'no entry', "doesn't list", 'does not list', 'not in the', 'not on the', 'no row', 'missing', 'not covered', 'retired', 'closed', 'merged']}, ensure_ascii=False))
