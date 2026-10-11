# DISTILL-CANARY-fe8a114e : distillation case
import csv, io, json, hashlib
c = json.load(open("case.json"))
for p,h in {'bindery/sheets.csv': 'f4c6a58196603754be59507a7ce52c647be7e3f0df11d023a7217ea7a51eeeeb', 'README.md': 'b266bee55f87ed74cc660258e80f263d77b30dd40960fc509bcc6e4d84dc3638'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
rows = list(csv.DictReader(io.StringIO(c["files"]['bindery/sheets.csv'])))
vals = [sum(int(r['sheets']) for r in rows if r['press'] == g) if 'aggregate' == "aggregate" else sum(r['press'] == g for r in rows) for g in ['Birch', 'Maple']]
for t, want in zip(c["turns"], [[str(vals[0])], [str(vals[1])], list(map(str, vals))]):
    assert t["expect"]["output_contains"] == want
print(json.dumps({"expected_number": vals[0]}))
