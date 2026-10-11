# DISTILL-CANARY-1205328f : distillation case
import csv, io, json, hashlib
c = json.load(open("case.json"))
for p,h in {'仓储/收货.csv': '96053ca7be62e70586de818487c2d987e940bfdeebdb3759720c86876c9d3578', 'README.md': 'b266bee55f87ed74cc660258e80f263d77b30dd40960fc509bcc6e4d84dc3638'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
rows = list(csv.DictReader(io.StringIO(c["files"]['仓储/收货.csv'])))
vals = [sum(int(r['crates']) for r in rows if r['zone'] == g) if 'aggregate' == "aggregate" else sum(r['zone'] == g for r in rows) for g in ['南仓', '北仓']]
for t, want in zip(c["turns"], [[str(vals[0])], [str(vals[1])], list(map(str, vals))]):
    assert t["expect"]["output_contains"] == want
print(json.dumps({"expected_number": vals[0]}))
