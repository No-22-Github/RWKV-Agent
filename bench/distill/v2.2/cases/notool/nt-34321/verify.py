# DISTILL-CANARY-7726d007 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '70b8762a2355a8adc4bd068c5c070b8b2a0bcc5f46f84ad72d4b05ca72a66d49', "fixture changed"
def compute():
    return [4500 * 0.38]

GIVEN = ["4500", "38%"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
