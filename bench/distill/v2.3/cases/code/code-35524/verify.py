# DISTILL-CANARY-43313f7e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5c3cb535f4b74fe24aa953184e3b9b10e00483bee4e72e4a0d5d5c225304684a', "fixture changed"
FACTS = json.loads('[{"line": "READ_TIMEOUT_S = 75", "decoy": "CONNECT_TIMEOUT_S = 10", "al": 314, "dl": 6}]')
ls = files['src/ledger/retry_policy.py'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_number": float('75')}))
