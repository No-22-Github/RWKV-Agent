# DISTILL-CANARY-b64aa90b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
assert files['energy/2026-09.csv'].splitlines()[0] == 'date,station,kwh,cost_eur'
assert files['stations/stations.csv'].splitlines()[0] == 'station_id,station,status,note'
ledger = list(csv.DictReader(io.StringIO(files['energy/2026-09.csv'])))
status = list(csv.DictReader(io.StringIO(files['stations/stations.csv'])))
assert ledger and set(ledger[0]) == set('date,station,kwh,cost_eur'.split(","))
assert not any(r['station'] == 'Old Mill Docks' for r in ledger)
codes = {r['station']: r for r in status}
row = codes['Old Mill Docks']
assert row['status'] == 'decommissioned' and 'Old Mill Crossing' in row['note']
decoy = sum(float(r['cost_eur']) for r in ledger if r['station'] == 'Old Mill Crossing')
exp = case["turns"][0]["expect"]["output_excludes"]
want = ["%.2f" % decoy, "{:,.2f}".format(decoy)]
assert all(w in exp for w in want)
print(json.dumps({"expected_contains_any": ['not listed', "isn't listed", 'no entry', "doesn't list", 'does not list', 'not in the', 'not on the', 'no row', 'missing', 'not covered', 'decommissioned', 'moved', 'no longer']}, ensure_ascii=False))
