# DISTILL-CANARY-e7ac715e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e9c2547a5e28ffde2d48d43af7260b7443f1126c4960cee97916a6ab46b337a6', "fixture changed"
def compute():
    import math
    return [int(math.log2(100000)) + 1]

GIVEN = ["100000"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
