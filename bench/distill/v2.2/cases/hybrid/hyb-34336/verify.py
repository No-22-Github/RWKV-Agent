# DISTILL-CANARY-de83ccbb : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bc033a741188157367e9837400642e6251362deeaed343eea94b415d9ecdead6', "fixture changed"
def compute():
    import math
    return [round(45 * math.tan(math.radians(32)) + 1.6, 2)]

GIVEN = ["45 米", "32 度", "1.6"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
