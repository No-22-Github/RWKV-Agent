# DISTILL-CANARY-a7bc6c9d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b80f78025a80645a6cb777be448075b1c81cdebc47228655c694e9a1ad442544', "fixture changed"
def compute():
    d = 468000 * 0.95
    return [round(d * 6 / 36, 2), round(d * 5 / 36, 2)]

GIVEN = ["468000", "5%", "8 年"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
