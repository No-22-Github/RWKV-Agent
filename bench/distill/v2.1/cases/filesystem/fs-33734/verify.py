# DISTILL-CANARY-4e9f801c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cbd0d47e5cc691c470890e197a0448e9b8f8a7e5ee8855f799ef5d3708c1b998', "fixture changed"
rows=[l.split() for l in files['listing.txt'].splitlines()]
w=sorted(r[2].split('/')[-1] for r in rows if r[0].startswith('2026-08') and int(r[1])>5000)
assert w==['jobs_a.csv','jobs_b.csv','jobs_d.csv','jobs_g.csv'], w
answers=['jobs_a.csv','jobs_d.csv']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
