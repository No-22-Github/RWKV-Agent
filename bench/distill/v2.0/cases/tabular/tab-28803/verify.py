# DISTILL-CANARY-c0036bab : distillation case
import csv, io, json, hashlib
c = json.load(open("case.json"))
for p,h in {'museum/visits.csv': 'f1f62bd620daa3f9b23fae2468966fd329afa6b64db94b2e019d2b1175dee372', 'README.md': 'b266bee55f87ed74cc660258e80f263d77b30dd40960fc509bcc6e4d84dc3638'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
rows = list(csv.DictReader(io.StringIO(c["files"]['museum/visits.csv'])))
vals = [sum(int(r['visitors']) for r in rows if r['wing'] == g) if 'aggregate' == "aggregate" else sum(r['wing'] == g for r in rows) for g in ['Glass', 'Stone']]
for t, want in zip(c["turns"], [[str(vals[0])], [str(vals[1])], list(map(str, vals))]):
    assert t["expect"]["output_contains"] == want
print(json.dumps({"expected_number": vals[0]}))
