# DISTILL-CANARY-c4cf5847 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '84783099e8dd133eb7aa31dae3cc748459a9cf8496ec4e485bb1ea956b64341b', "fixture changed"
FACTS = json.loads('[{"line": "raise ChecksumMismatchError(", "decoy": "raise SchemaViolation(", "al": 337, "dl": 11}]')
ls = files['src/ingest/manifest_check.py'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_string": 'ChecksumMismatchError'}, ensure_ascii=False))
