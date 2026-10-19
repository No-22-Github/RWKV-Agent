# DISTILL-CANARY-2616f7e2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3a272baa7914fe6347e1bc62d70f131d21943550b0855944ca3fd66fb42a7424', "fixture changed"
def compute():
    return [250 / 12 * 30, 250 / 12 * 18]

GIVEN = ["250", "12", "30", "18"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
