# DISTILL-CANARY-48e04fe7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
assert files['rides/2026-09.csv'].splitlines()[0] == 'date,station,rides'
assert files['stations/stations.csv'].splitlines()[0] == 'station_id,station,status,note'
ledger = list(csv.DictReader(io.StringIO(files['rides/2026-09.csv'])))
status = list(csv.DictReader(io.StringIO(files['stations/stations.csv'])))
assert ledger and set(ledger[0]) == set('date,station,rides'.split(","))
assert not any(r['station'] == 'Cannery Wharf' for r in ledger)
codes = {r['station']: r for r in status}
row = codes['Cannery Wharf']
assert row['status'] == 'removed' and 'Cannery Wharf North' in row['note']
decoy = sum(float(r['rides']) for r in ledger if r['station'] == 'Cannery Wharf North')
exp = case["turns"][0]["expect"]["output_excludes"]
n = int(round(decoy))
want = [str(n), "{:,}".format(n)]
assert all(w in exp for w in want)
print(json.dumps({"expected_contains_any": ['not listed', "isn't listed", 'no entry', "doesn't list", 'does not list', 'not in the', 'not on the', 'no row', 'missing', 'not covered', 'removed', 'redistributed', 'taken out of service', 'decommissioned']}, ensure_ascii=False))
