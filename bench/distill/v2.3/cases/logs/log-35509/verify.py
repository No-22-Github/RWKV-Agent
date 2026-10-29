# DISTILL-CANARY-4cfd9897 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4736c1c34ce997c146e07d3e3b6f308c4a12c233679cd61d3a43c87f95d83f5f', "fixture changed"
FACTS = json.loads('[{"line": "job=nightly-compaction failed", "decoy": "job=nightly-rollup retry", "al": 392, "dl": 71}]')
ls = files['logs/ingest-worker-0914.log'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('137')}))
