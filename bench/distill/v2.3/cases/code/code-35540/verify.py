# DISTILL-CANARY-2e0dd642 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '619721ca3aec1ec12552dfb528785c5c43f4a1661e27f7f5274eff5ec254a1cc', "fixture changed"
FACTS = json.loads('[{"line": "package telemetry", "decoy": "legacy package metricsv1", "al": 1, "dl": 307}, {"line": "\\t\\"context\\"", "decoy": "net/http/pprof", "al": 4, "dl": 389}]')
ls = files['internal/metrics/exporter.go'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] < 60 and f["dl"] > 230
print(json.dumps({"expected_string": 'telemetry'}, ensure_ascii=False))
