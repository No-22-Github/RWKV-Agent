# DISTILL-CANARY-8e6df460 : distillation case
import csv, io, json, hashlib
c = json.load(open("case.json"))
for p,h in {'剧场/签收.csv': '9045d13145a320c51c9c034a0ef9f58f42c18e0be3fa503cfbc41e85df7c6a2b', 'README.md': 'b266bee55f87ed74cc660258e80f263d77b30dd40960fc509bcc6e4d84dc3638'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
rows = list(csv.DictReader(io.StringIO(c["files"]['剧场/签收.csv'])))
vals = [sum(int(r['pieces']) for r in rows if r['section'] == g) if 'filter_count' == "aggregate" else sum(r['section'] == g for r in rows) for g in ['服装', '道具']]
for t, want in zip(c["turns"], [[str(vals[0])], [str(vals[1])], list(map(str, vals))]):
    assert t["expect"]["output_contains"] == want
print(json.dumps({"expected_number": vals[0]}))
