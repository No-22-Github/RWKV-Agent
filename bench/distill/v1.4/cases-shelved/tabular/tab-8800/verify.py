# DISTILL-CANARY-213e9ba8 : distillation case
import csv, io, json, hashlib
c = json.load(open("case.json"))
for p,h in {'维修/工单.csv': '361d9f898ec7068786e2ae2ceb6de5610cb040436d60ed46534a8ef22243de2d', 'README.md': 'b266bee55f87ed74cc660258e80f263d77b30dd40960fc509bcc6e4d84dc3638'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
rows = list(csv.DictReader(io.StringIO(c["files"]['维修/工单.csv'])))
vals = [sum(int(r['minutes']) for r in rows if r['team'] == g) if 'aggregate' == "aggregate" else sum(r['team'] == g for r in rows) for g in ['机修', '电检']]
for t, want in zip(c["turns"], [[str(vals[0])], [str(vals[1])], list(map(str, vals))]):
    assert t["expect"]["output_contains"] == want
print(json.dumps({"expected_number": vals[0]}))
