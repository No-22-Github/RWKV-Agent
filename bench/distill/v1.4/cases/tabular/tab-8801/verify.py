# DISTILL-CANARY-7abbbd32 : distillation case
import csv, io, json, hashlib
c = json.load(open("case.json"))
for p,h in {'library/returns.csv': 'b4270b5fbfb92895c539e3a2589cf83e193a16f10e014e00bc7664932a7cb159', 'README.md': 'b266bee55f87ed74cc660258e80f263d77b30dd40960fc509bcc6e4d84dc3638'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
rows = list(csv.DictReader(io.StringIO(c["files"]['library/returns.csv'])))
vals = [sum(int(r['books']) for r in rows if r['desk'] == g) if 'aggregate' == "aggregate" else sum(r['desk'] == g for r in rows) for g in ['West', 'East']]
for t, want in zip(c["turns"], [[str(vals[0])], [str(vals[1])], list(map(str, vals))]):
    assert t["expect"]["output_contains"] == want
print(json.dumps({"expected_number": vals[0]}))
