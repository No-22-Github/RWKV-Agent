# DISTILL-CANARY-8c0029c6 : distillation case
import csv, io, json, hashlib
c = json.load(open("case.json"))
for p,h in {'诊所/配药.csv': '287fe7c7c9de64e064176a4ce57da317c1ddf815f8eae0ce46aa1c4a509da20e', 'README.md': 'b266bee55f87ed74cc660258e80f263d77b30dd40960fc509bcc6e4d84dc3638'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
rows = list(csv.DictReader(io.StringIO(c["files"]['诊所/配药.csv'])))
vals = [sum(int(r['盒数']) for r in rows if r['柜台'] == g) if 'aggregate' == "aggregate" else sum(r['柜台'] == g for r in rows) for g in ['东柜', '西柜']]
for t, want in zip(c["turns"], [[str(vals[0])], [str(vals[1])], list(map(str, vals))]):
    assert t["expect"]["output_contains"] == want
print(json.dumps({"expected_number": vals[0]}))
