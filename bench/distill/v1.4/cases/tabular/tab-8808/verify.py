# DISTILL-CANARY-eff22746 : distillation case
import csv, io, json, hashlib
c = json.load(open("case.json"))
for p,h in {'育苗/入盘.csv': 'fa1cebe0197f398ff52b96aa8d29a41010988ded43950fd1b5219f6f56a65871', 'README.md': 'b266bee55f87ed74cc660258e80f263d77b30dd40960fc509bcc6e4d84dc3638'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
rows = list(csv.DictReader(io.StringIO(c["files"]['育苗/入盘.csv'])))
vals = [sum(int(r['盘数']) for r in rows if r['棚区'] == g) if 'filter_count' == "aggregate" else sum(r['棚区'] == g for r in rows) for g in ['甲棚', '乙棚']]
for t, want in zip(c["turns"], [[str(vals[0])], [str(vals[1])], list(map(str, vals))]):
    assert t["expect"]["output_contains"] == want
print(json.dumps({"expected_number": vals[0]}))
