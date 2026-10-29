# DISTILL-CANARY-24642d2f : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c461784ad72e9e8109f0d3628fc4050f4d1b9ea1d5b90a6c7717b5cbc0f97b50', "fixture changed"
FACTS = json.loads('[{"line": "max_concurrent_jobs = 48", "decoy": "max_concurrent_jobs = 16", "al": 356, "dl": 58}]')
ls = files['config/scheduler-limits.toml'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('48')}))
