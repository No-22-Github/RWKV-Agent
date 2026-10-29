# DISTILL-CANARY-0f9967eb : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ebdfcf8c29d67b88a7304336e693bd942cad253300ece2ffa9e4a421f5b18cf5', "fixture changed"
FACTS = json.loads('[{"line": "const defaultMaxInflight = 128", "decoy": "const defaultBatchSize = 32", "al": 313, "dl": 8}]')
ls = files['internal/queue/dispatcher.go'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('128')}))
