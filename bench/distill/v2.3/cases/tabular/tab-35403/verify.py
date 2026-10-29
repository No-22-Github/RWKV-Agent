# DISTILL-CANARY-38be9071 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '46c411031ab544bb2e7212aef7d385e79a3bce8bf37e4f38582877fb4be1a214', "fixture changed"
def truth(files):
    rows = [l.split(",") for l in files["sales/regional-roll-2026h1.csv"].strip().split("\n")[1:]]
    tot = {}
    for r in rows:
        tot[r[1]] = tot.get(r[1], 0) + int(r[3])
    best = max(tot, key=tot.get)
    return {"numbers": [float(tot[best]), float(round(tot[best] / 6))], "strings": [best]}

got = truth(case["files"])
nums = got.get("numbers")
if nums is not None:
    tn = [t for t in case["turns"] if "expected_number" in t["expect"]]
    assert len(tn) == len(nums)
    for t, x in zip(tn, nums):
        assert abs(t["expect"]["expected_number"] - x) < 1e-9
for p, txt in (got.get("files") or {}).items():
    assert case["expect"]["files"][p]["equals"] == txt
for s in got.get("strings", []):
    assert any(s in t["expect"].get("output_contains", []) for t in case["turns"])
if got.get("files"):
    print(json.dumps({"files": got["files"]}, ensure_ascii=False))
elif nums is not None:
    print(json.dumps({"expected_number": float(nums[0])}))
else:
    print(json.dumps({"expected_string": got["strings"][0]}, ensure_ascii=False))
