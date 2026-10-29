# DISTILL-CANARY-1c6861ae : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd8b6b19a9beca6536696ebacbfa3bb6516bb4832437c2038d41bfdf5805091a9', "fixture changed"
def truth(files):
    rows = [l.split(",") for l in files["人事/技术部薪资明细-2026.csv"].strip().split("\n")[1:]]
    xs = [int(r[2]) for r in rows if r[1] == "P6"]
    return {"numbers": [round(sum(xs) / len(xs), 1)]}

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
