# DISTILL-CANARY-f0a6ba7c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
def compute():
    i = 0.045 / 12
    n = 96
    a = 60000 * i / ((1 + i) ** n - 1)
    j = 0.035 / 12
    b = 60000 * j / ((1 + j) ** n - 1)
    return [round(a, 2), round(b, 2)]

GIVEN = ["60,000", "4.5%", "3.5%"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
