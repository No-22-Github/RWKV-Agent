# DISTILL-CANARY-b15fa064 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bc033a741188157367e9837400642e6251362deeaed343eea94b415d9ecdead6', "fixture changed"
def compute():
    import math
    return [round(math.log(2) / math.log(1.0425), 2)]

GIVEN = ["4.25%"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
