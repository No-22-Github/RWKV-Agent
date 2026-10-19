# DISTILL-CANARY-c5829c0d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0e33cf3195a452eb211ad67c1fc38b8d184e38760887d85d098308b42defb672', "fixture changed"
def compute():
    import math
    a, b, c = 13.7, 21.4, 18.9
    s = (a + b + c) / 2
    return [round(math.sqrt(s * (s - a) * (s - b) * (s - c)), 2)]

GIVEN = ["13.7", "21.4", "18.9"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
