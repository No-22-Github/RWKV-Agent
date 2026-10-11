# DISTILL-CANARY-e274ae2e : distillation case
import csv, io, json, hashlib
c = json.load(open("case.json"))
for p,h in {'harbor/checks.csv': '088d2c33b3a4434a3ac869b11c3d830019129455b627a276adfc4f9522f30280', 'README.md': 'b266bee55f87ed74cc660258e80f263d77b30dd40960fc509bcc6e4d84dc3638'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
rows = list(csv.DictReader(io.StringIO(c["files"]['harbor/checks.csv'])))
vals = [sum(int(r['checks']) for r in rows if r['berth'] == g) if 'filter_count' == "aggregate" else sum(r['berth'] == g for r in rows) for g in ['Reed', 'Slate']]
for t, want in zip(c["turns"], [[str(vals[0])], [str(vals[1])], list(map(str, vals))]):
    assert t["expect"]["output_contains"] == want
print(json.dumps({"expected_number": vals[0]}))
