# DISTILL-CANARY-3f3ea10b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c44aab3105d10d71a59720e75765cd1ada97c158623cfeb04e0a92c4e18f78a2', "fixture changed"
def truth(files):
    import datetime
    import re
    s = re.search(r"Lease start: (\d{4}-\d\d-\d\d)", files["contracts/harlow-lease-terms.txt"]).group(1)
    d = datetime.date.fromisoformat(s) + datetime.timedelta(days=100)
    return {"strings": [d.isoformat()]}

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
